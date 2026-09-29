from datetime import datetime

from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, abort, current_app
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from app import db
from app.models.lead import Lead
from app.models.payment import Payment
from app.models.membership import Membership
from app.utils.decorators import role_required
from app.utils.logger import get_audit_logger

admin_bp = Blueprint('admin', __name__)
audit = get_audit_logger()


# ------------------------------------------------------------------
# Forms
# ------------------------------------------------------------------
class LeadUpdateForm(FlaskForm):
    status = SelectField(
        'Status',
        choices=[(s, s.title()) for s in Lead.STATUS_CHOICES],
        validators=[DataRequired()]
    )
    notes = TextAreaField('Internal Notes', validators=[Optional(), Length(max=2000)])
    submit = SubmitField('Update Lead')


class PaymentDecisionForm(FlaskForm):
    admin_note = TextAreaField('Note (optional)', validators=[Optional(), Length(max=255)])
    verify = SubmitField('Verify & Activate')
    reject = SubmitField('Reject')


# ------------------------------------------------------------------
# Leads
# ------------------------------------------------------------------
@admin_bp.route('/leads')
@login_required
@role_required('admin')
def leads():
    status_filter = request.args.get('status', '').strip().lower()
    q = Lead.query
    if status_filter in Lead.STATUS_CHOICES:
        q = q.filter_by(status=status_filter)
    leads = q.order_by(Lead.created_at.desc()).limit(200).all()

    counts = {s: Lead.query.filter_by(status=s).count() for s in Lead.STATUS_CHOICES}
    counts['all'] = Lead.query.count()
    return render_template('admin/leads.html', leads=leads,
                           counts=counts, status_filter=status_filter)


@admin_bp.route('/leads/<int:lead_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def lead_detail(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if lead is None:
        abort(404)

    form = LeadUpdateForm(obj=lead)
    if form.validate_on_submit():
        old = lead.status
        new = form.status.data
        if new not in Lead.STATUS_CHOICES:
            abort(400)
        lead.status = new
        lead.notes = (form.notes.data or '').strip()
        if new != 'new' and lead.handled_by_id is None:
            lead.handled_by_id = current_user.id
            lead.handled_at = datetime.utcnow()
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception('LEAD_UPDATE_FAILED lead_id=%s', lead.id)
            flash('Could not update lead.', 'danger')
            return render_template('admin/lead_detail.html', lead=lead, form=form), 500
        audit.info('LEAD_UPDATED lead_id=%s old=%s new=%s by=%s',
                   lead.id, old, new, current_user.email)
        flash('Lead updated.', 'success')
        return redirect(url_for('admin.lead_detail', lead_id=lead.id))

    return render_template('admin/lead_detail.html', lead=lead, form=form)


# ------------------------------------------------------------------
# Payments queue
# ------------------------------------------------------------------
@admin_bp.route('/payments')
@login_required
@role_required('admin')
def payments():
    status_filter = request.args.get('status', 'submitted').strip().lower()
    if status_filter not in Payment.STATUS_CHOICES and status_filter != 'all':
        status_filter = 'submitted'

    q = Payment.query
    if status_filter != 'all':
        q = q.filter_by(status=status_filter)
    payments = q.order_by(Payment.created_at.desc()).limit(200).all()

    counts = {s: Payment.query.filter_by(status=s).count() for s in Payment.STATUS_CHOICES}
    counts['all'] = Payment.query.count()

    return render_template('admin/payments.html', payments=payments,
                           counts=counts, status_filter=status_filter)


@admin_bp.route('/payments/<int:payment_id>/verify', methods=['POST'])
@login_required
@role_required('admin')
def payment_verify(payment_id: int):
    payment = db.session.get(Payment, payment_id)
    if payment is None:
        abort(404)
    if payment.status != 'submitted':
        flash('This payment has already been processed.', 'warning')
        return redirect(url_for('admin.payments'))

    form = PaymentDecisionForm()
    if not form.validate_on_submit():
        abort(400)

    membership = payment.membership
    now = datetime.utcnow()

    try:
        payment.status = 'verified'
        payment.verified_by_id = current_user.id
        payment.verified_at = now
        payment.admin_note = (form.admin_note.data or '').strip()

        membership.status = 'active'
        membership.started_at = now
        membership.expires_at = membership.compute_expiry(now)
        membership.activated_by_id = current_user.id
        membership.activated_at = now

        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception('PAYMENT_VERIFY_FAILED payment_id=%s', payment_id)
        flash('Could not verify payment. See logs.', 'danger')
        return redirect(url_for('admin.payments'))

    audit.info('PAYMENT_VERIFIED payment_id=%s user_id=%s utr=%s by=%s expires=%s',
               payment.id, payment.user_id, payment.utr_reference,
               current_user.email, membership.expires_at.isoformat())

    flash(f'Payment verified. Membership activated until '
          f'{membership.expires_at.strftime("%Y-%m-%d")}.', 'success')
    return redirect(url_for('admin.payments'))


@admin_bp.route('/payments/<int:payment_id>/reject', methods=['POST'])
@login_required
@role_required('admin')
def payment_reject(payment_id: int):
    payment = db.session.get(Payment, payment_id)
    if payment is None:
        abort(404)
    if payment.status != 'submitted':
        flash('This payment has already been processed.', 'warning')
        return redirect(url_for('admin.payments'))

    form = PaymentDecisionForm()
    if not form.validate_on_submit():
        abort(400)

    try:
        payment.status = 'rejected'
        payment.verified_by_id = current_user.id
        payment.verified_at = datetime.utcnow()
        payment.admin_note = (form.admin_note.data or '').strip()
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception('PAYMENT_REJECT_FAILED payment_id=%s', payment_id)
        flash('Could not reject payment. See logs.', 'danger')
        return redirect(url_for('admin.payments'))

    audit.info('PAYMENT_REJECTED payment_id=%s user_id=%s utr=%s by=%s',
               payment.id, payment.user_id, payment.utr_reference,
               current_user.email)
    flash('Payment rejected. Member can resubmit.', 'info')
    return redirect(url_for('admin.payments'))
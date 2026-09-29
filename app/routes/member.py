from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, abort, current_app, send_file, request
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Optional

from app import db
from app.models.plan import Plan
from app.models.membership import Membership
from app.models.payment import Payment
from app.services.upi import build_upi_uri, build_qr_png_bytes
from app.utils.logger import get_audit_logger

from io import BytesIO

member_bp = Blueprint('member', __name__)
audit = get_audit_logger()


# ------------------------------------------------------------------
# Forms
# ------------------------------------------------------------------
class PaymentSubmitForm(FlaskForm):
    utr_reference = StringField(
        'UTR / Reference Number',
        validators=[
            DataRequired(),
            Length(min=6, max=60),
            Regexp(r'^[A-Za-z0-9\-]+$',
                   message='Only letters, numbers, and hyphens allowed'),
        ]
    )
    member_note = StringField(
        'Note (optional)',
        validators=[Optional(), Length(max=255)]
    )
    submit = SubmitField('Submit Payment')


# ------------------------------------------------------------------
# Plans
# ------------------------------------------------------------------
@member_bp.route('/plans')
@login_required
def plans():
    available = (
        Plan.query
        .filter_by(is_active=True)
        .order_by(Plan.sort_order.asc(), Plan.price_paise.asc())
        .all()
    )
    return render_template(
        'member/plans.html',
        plans=available,
        membership=current_user.membership,
    )


@member_bp.route('/select-plan/<int:plan_id>', methods=['POST'])
@login_required
def select_plan(plan_id: int):
    plan = db.session.get(Plan, plan_id)
    if plan is None or not plan.is_active:
        abort(404)

    membership = current_user.membership

    if membership is None:
        membership = Membership(
            user_id=current_user.id,
            plan_id=plan.id,
            status='pending',
        )
        db.session.add(membership)
        audit.info('MEMBERSHIP_CREATED user_id=%s plan=%s',
                   current_user.id, plan.code)
        flash(f'Plan "{plan.name}" selected. Please complete payment to activate.',
              'success')
    else:
        if not membership.can_change_plan():
            audit.warning('MEMBERSHIP_CHANGE_DENIED user_id=%s status=%s',
                          current_user.id, membership.status)
            flash('Your membership is not editable in its current state.', 'danger')
            return redirect(url_for('member.membership'))

        old_plan_id = membership.plan_id
        membership.plan_id = plan.id
        audit.info('MEMBERSHIP_PLAN_CHANGED user_id=%s old_plan=%s new_plan=%s',
                   current_user.id, old_plan_id, plan.code)
        flash(f'Plan changed to "{plan.name}".', 'success')

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception('MEMBERSHIP_SAVE_FAILED user_id=%s', current_user.id)
        flash('Could not save your plan. Please try again.', 'danger')
        return redirect(url_for('member.plans'))

    return redirect(url_for('member.membership'))


# ------------------------------------------------------------------
# Membership overview
# ------------------------------------------------------------------
@member_bp.route('/membership')
@login_required
def membership():
    payments = (
        Payment.query
        .filter_by(user_id=current_user.id)
        .order_by(Payment.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template(
        'member/membership.html',
        membership=current_user.membership,
        payments=payments,
    )


# ------------------------------------------------------------------
# Payment: show instructions + submit UTR
# ------------------------------------------------------------------
@member_bp.route('/payment', methods=['GET'])
@login_required
def payment():
    membership = current_user.membership
    if membership is None:
        flash('Please choose a plan first.', 'warning')
        return redirect(url_for('member.plans'))

    if membership.status == 'active':
        flash('Your membership is already active.', 'info')
        return redirect(url_for('member.membership'))

    if membership.status not in ('pending',):
        flash('Payment is not available for your membership state.', 'warning')
        return redirect(url_for('member.membership'))

    # Check for an existing submitted payment (still awaiting admin)
    existing = (
        Payment.query
        .filter_by(user_id=current_user.id, membership_id=membership.id,
                   status='submitted')
        .order_by(Payment.created_at.desc())
        .first()
    )

    amount_paise = membership.plan.price_paise
    upi_uri = build_upi_uri(
        amount_paise=amount_paise,
        note=f'{membership.plan.name} membership',
        txn_ref=f'GYM-{membership.user_id}-{membership.plan_id}',
    )

    form = PaymentSubmitForm()

    return render_template(
        'member/payment.html',
        membership=membership,
        existing=existing,
        upi_uri=upi_uri,
        amount_paise=amount_paise,
        form=form,
    )


@member_bp.route('/payment/qr.png')
@login_required
def payment_qr():
    """Stream the QR code PNG for the member's pending membership."""
    membership = current_user.membership
    if membership is None or membership.status != 'pending':
        abort(404)

    amount_paise = membership.plan.price_paise
    upi_uri = build_upi_uri(
        amount_paise=amount_paise,
        note=f'{membership.plan.name} membership',
        txn_ref=f'GYM-{membership.user_id}-{membership.plan_id}',
    )
    png = build_qr_png_bytes(upi_uri)
    return send_file(BytesIO(png), mimetype='image/png',
                     download_name='upi-qr.png')


@member_bp.route('/payment/submit', methods=['POST'])
@login_required
def payment_submit():
    membership = current_user.membership
    if membership is None or membership.status != 'pending':
        flash('No pending membership to pay for.', 'warning')
        return redirect(url_for('member.membership'))

    form = PaymentSubmitForm()
    if not form.validate_on_submit():
        flash('Please fix the errors in the payment form.', 'warning')
        return redirect(url_for('member.payment'))

    utr = form.utr_reference.data.strip().upper()
    note = (form.member_note.data or '').strip()

    # Prevent duplicates across the whole system
    if Payment.query.filter_by(utr_reference=utr).first():
        audit.warning('PAYMENT_DUPLICATE_UTR user_id=%s utr=%s',
                      current_user.id, utr)
        flash('This UTR has already been submitted. Please check with support.',
              'danger')
        return redirect(url_for('member.payment'))

    payment = Payment(
        user_id=current_user.id,
        membership_id=membership.id,
        amount_paise=membership.plan.price_paise,
        utr_reference=utr,
        member_note=note,
        status='submitted',
    )

    try:
        db.session.add(payment)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception('PAYMENT_SUBMIT_FAILED user_id=%s utr=%s',
                                     current_user.id, utr)
        flash('Could not submit payment. Please try again.', 'danger')
        return redirect(url_for('member.payment'))

    audit.info('PAYMENT_SUBMITTED payment_id=%s user_id=%s utr=%s amount=%s',
               payment.id, current_user.id, utr, payment.amount_paise)
    flash('Payment submitted. Admin will verify shortly.', 'success')
    return redirect(url_for('member.membership'))
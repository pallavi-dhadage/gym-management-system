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
from app.utils.decorators import role_required
from app.utils.logger import get_audit_logger

admin_bp = Blueprint('admin', __name__)
audit = get_audit_logger()


class LeadUpdateForm(FlaskForm):
    status = SelectField(
        'Status',
        choices=[(s, s.title()) for s in Lead.STATUS_CHOICES],
        validators=[DataRequired()]
    )
    notes = TextAreaField(
        'Internal Notes',
        validators=[Optional(), Length(max=2000)]
    )
    submit = SubmitField('Update Lead')


@admin_bp.route('/leads')
@login_required
@role_required('admin')
def leads():
    status_filter = request.args.get('status', '').strip().lower()

    q = Lead.query
    if status_filter in Lead.STATUS_CHOICES:
        q = q.filter_by(status=status_filter)

    leads = q.order_by(Lead.created_at.desc()).limit(200).all()

    counts = {
        s: Lead.query.filter_by(status=s).count()
        for s in Lead.STATUS_CHOICES
    }
    counts['all'] = Lead.query.count()

    return render_template(
        'admin/leads.html',
        leads=leads,
        counts=counts,
        status_filter=status_filter,
    )


@admin_bp.route('/leads/<int:lead_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def lead_detail(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if lead is None:
        abort(404)

    form = LeadUpdateForm(obj=lead)

    if form.validate_on_submit():
        old_status = lead.status
        new_status = form.status.data

        if new_status not in Lead.STATUS_CHOICES:
            abort(400)

        lead.status = new_status
        lead.notes = (form.notes.data or '').strip()

        if new_status != 'new' and lead.handled_by_id is None:
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
                   lead.id, old_status, new_status, current_user.email)
        flash('Lead updated.', 'success')
        return redirect(url_for('admin.lead_detail', lead_id=lead.id))

    return render_template('admin/lead_detail.html', lead=lead, form=form)
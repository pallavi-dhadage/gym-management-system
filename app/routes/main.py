from flask import (
    Blueprint, render_template, current_app,
    request, redirect, url_for, flash
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, Optional

from app import db, limiter
from app.models.lead import Lead
from app.models.plan import Plan
from app.utils.logger import get_audit_logger

main_bp = Blueprint('main', __name__)
audit = get_audit_logger()


class EnquiryForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField(
        'Phone',
        validators=[DataRequired(), Regexp(r'^\+?[0-9]{7,15}$', message='Enter a valid phone number')]
    )
    message = TextAreaField('Message', validators=[Optional(), Length(max=2000)])
    website = StringField('Website', validators=[Optional()])
    submit = SubmitField('Send Enquiry')


def _active_plans():
    return (
        Plan.query
        .filter_by(is_active=True)
        .order_by(Plan.sort_order.asc(), Plan.price_paise.asc())
        .all()
    )


@main_bp.route('/')
def index():
    current_app.logger.info('Landing page visited')
    return render_template('index.html', form=EnquiryForm(), plans=_active_plans())


@main_bp.route('/pricing')
def pricing():
    return render_template('pricing.html', plans=_active_plans())


@main_bp.route('/enquiry', methods=['GET', 'POST'])
@limiter.limit('5 per hour', methods=['POST'])
def enquiry():
    form = EnquiryForm()

    if form.validate_on_submit():
        if form.website.data:
            audit.warning('ENQUIRY_HONEYPOT email=%s ip=%s',
                          form.email.data, request.remote_addr)
            flash('Thanks! We will reach out shortly.', 'success')
            return redirect(url_for('main.index'))

        lead = Lead(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip(),
            message=(form.message.data or '').strip(),
            source='landing_page',
            ip_address=request.remote_addr,
            user_agent=(request.user_agent.string or '')[:255],
        )

        try:
            db.session.add(lead)
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception('ENQUIRY_CREATE_FAILED email=%s', lead.email)
            flash('Could not submit enquiry. Please try again.', 'danger')
            return render_template('index.html', form=form, plans=_active_plans()), 500

        audit.info('LEAD_CREATED lead_id=%s email=%s ip=%s',
                   lead.id, lead.email, request.remote_addr)
        flash('Thanks! We will reach out shortly.', 'success')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        flash('Please fix the errors in the form.', 'warning')

    return render_template('index.html', form=form, plans=_active_plans())


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)
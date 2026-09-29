from datetime import datetime
from urllib.parse import urlparse

from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

from app import db, limiter
from app.models.user import User
from app.models.plan import Plan
from app.models.membership import Membership
from app.utils.logger import get_audit_logger

auth_bp = Blueprint('auth', __name__)
audit = get_audit_logger()


class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField(
        'Phone',
        validators=[DataRequired(), Regexp(r'^\+?[0-9]{7,15}$', message='Enter a valid phone number')]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(), Length(min=8, max=128),
            Regexp(r'^(?=.*[A-Za-z])(?=.*\d).+$',
                   message='Password must contain at least one letter and one number')
        ]
    )
    confirm = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


def _is_safe_url(target: str) -> bool:
    if not target:
        return False
    ref = urlparse(request.host_url)
    test = urlparse(target)
    return test.scheme in ('http', 'https') and ref.netloc == test.netloc


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit('10 per hour', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegisterForm()

    # Pre-select plan from query string (e.g. from pricing page)
    plan_id_raw = request.args.get('plan', type=int)
    preselected_plan = None
    if plan_id_raw:
        preselected_plan = db.session.get(Plan, plan_id_raw)
        if preselected_plan and not preselected_plan.is_active:
            preselected_plan = None

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        if User.query.filter_by(email=email).first():
            audit.info('REGISTER_DUPLICATE email=%s ip=%s', email, request.remote_addr)
            flash('An account with this email already exists.', 'danger')
            return render_template('auth/register.html', form=form,
                                   preselected_plan=preselected_plan), 400

        user = User(
            email=email,
            full_name=form.full_name.data.strip(),
            phone=form.phone.data.strip(),
            role='member',
        )
        user.set_password(form.password.data)

        # Also pick up plan_id from a hidden form field (safer than only query)
        form_plan_id = request.form.get('plan_id', type=int)
        if form_plan_id:
            form_plan = db.session.get(Plan, form_plan_id)
            if form_plan and form_plan.is_active:
                preselected_plan = form_plan

        try:
            db.session.add(user)
            db.session.flush()   # get user.id

            if preselected_plan:
                membership = Membership(
                    user_id=user.id,
                    plan_id=preselected_plan.id,
                    status='pending',
                )
                db.session.add(membership)
                audit.info('MEMBERSHIP_CREATED user_id=%s plan=%s (at registration)',
                           user.id, preselected_plan.code)

            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception('REGISTER_FAILED email=%s', email)
            flash('Registration failed. Please try again.', 'danger')
            return render_template('auth/register.html', form=form,
                                   preselected_plan=preselected_plan), 500

        audit.info('REGISTER_SUCCESS user_id=%s email=%s ip=%s',
                   user.id, user.email, request.remote_addr)
        current_app.logger.info('New user registered: %s', user.email)

        if preselected_plan:
            flash(f'Account created with "{preselected_plan.name}" plan (pending payment).', 'success')
        else:
            flash('Account created. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form,
                           preselected_plan=preselected_plan)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('20 per hour', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            audit.warning('LOGIN_FAIL email=%s ip=%s ua="%s"',
                          email, request.remote_addr,
                          request.user_agent.string[:100])
            current_app.logger.warning('Failed login attempt for %s', email)
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html', form=form), 401

        if not user.is_active_account:
            audit.warning('LOGIN_BLOCKED_INACTIVE user_id=%s ip=%s',
                          user.id, request.remote_addr)
            flash('Your account is disabled. Contact support.', 'danger')
            return render_template('auth/login.html', form=form), 403

        login_user(user, remember=bool(form.remember.data))
        user.last_login_at = datetime.utcnow()
        db.session.commit()

        audit.info('LOGIN_SUCCESS user_id=%s email=%s ip=%s',
                   user.id, user.email, request.remote_addr)
        current_app.logger.info('User logged in: %s', user.email)

        next_url = request.args.get('next')
        if next_url and _is_safe_url(next_url):
            return redirect(next_url)
        return redirect(url_for('main.dashboard'))

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    user_id = current_user.id
    email = current_user.email
    logout_user()
    audit.info('LOGOUT user_id=%s email=%s ip=%s',
               user_id, email, request.remote_addr)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
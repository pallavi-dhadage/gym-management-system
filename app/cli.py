import click
from flask.cli import with_appcontext
from flask import current_app

from app import db
from app.models.user import User
from app.models.plan import Plan
from app.utils.logger import get_audit_logger


@click.command('create-admin')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--full-name', prompt='Full name', help='Admin full name')
@click.option('--phone', prompt=True, help='Admin phone')
@click.option(
    '--password',
    prompt=True, hide_input=True, confirmation_prompt=True,
    help='Admin password (min 8 chars, letters + numbers)'
)
@with_appcontext
def create_admin_command(email, full_name, phone, password):
    """Create an admin user from the command line."""
    audit = get_audit_logger()

    email = email.strip().lower()
    if len(password) < 8 or not any(c.isalpha() for c in password) \
            or not any(c.isdigit() for c in password):
        click.echo('ERROR: Password must be at least 8 chars and contain letters and numbers.')
        raise SystemExit(1)

    existing = User.query.filter_by(email=email).first()
    if existing:
        if existing.role == 'admin':
            click.echo(f'Admin already exists: {email}')
            return
        existing.role = 'admin'
        db.session.commit()
        audit.info('ADMIN_PROMOTED user_id=%s email=%s', existing.id, email)
        click.echo(f'Promoted existing user to admin: {email}')
        return

    user = User(email=email, full_name=full_name.strip(),
                phone=phone.strip(), role='admin')
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception('CREATE_ADMIN_FAILED email=%s', email)
        click.echo('ERROR: Could not create admin. See logs.')
        raise SystemExit(1)

    audit.info('ADMIN_CREATED user_id=%s email=%s', user.id, email)
    click.echo(f'Admin created: {email} (id={user.id})')


@click.command('list-users')
@with_appcontext
def list_users_command():
    """List all users (id, email, role, active)."""
    users = User.query.order_by(User.id).all()
    if not users:
        click.echo('No users yet.')
        return
    click.echo(f'{"ID":<5} {"EMAIL":<35} {"ROLE":<10} {"ACTIVE":<7} NAME')
    for u in users:
        click.echo(f'{u.id:<5} {u.email:<35} {u.role:<10} '
                   f'{str(u.is_active_account):<7} {u.full_name}')


@click.command('seed-plans')
@with_appcontext
def seed_plans_command():
    """Seed the default membership plans (idempotent)."""
    defaults = [
        dict(
            code='basic-30',
            name='Basic Monthly',
            description='Gym access for 30 days.',
            price_paise=99900,
            duration_days=30,
            sort_order=1,
        ),
        dict(
            code='pro-90',
            name='Pro Quarterly',
            description='Gym + 2 PT sessions per month, 90 days.',
            price_paise=249900,
            duration_days=90,
            sort_order=2,
        ),
        dict(
            code='elite-365',
            name='Elite Yearly',
            description='Gym + weekly PT + diet plan, 365 days.',
            price_paise=899900,
            duration_days=365,
            sort_order=3,
        ),
    ]

    created = 0
    for spec in defaults:
        existing = Plan.query.filter_by(code=spec['code']).first()
        if existing:
            continue
        db.session.add(Plan(**spec))
        created += 1

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception('SEED_PLANS_FAILED')
        click.echo('ERROR: could not seed plans. See logs.')
        raise SystemExit(1)

    click.echo(f'Seeded {created} plan(s). Total plans: {Plan.query.count()}')


def register_cli(app):
    app.cli.add_command(create_admin_command)
    app.cli.add_command(list_users_command)
    app.cli.add_command(seed_plans_command)
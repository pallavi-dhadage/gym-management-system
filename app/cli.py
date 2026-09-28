import click
from flask.cli import with_appcontext
from flask import current_app

from app import db
from app.models.user import User
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


def register_cli(app):
    app.cli.add_command(create_admin_command)
    app.cli.add_command(list_users_command)

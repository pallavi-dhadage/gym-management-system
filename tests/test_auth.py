from app.models.user import User
from app import db
from tests.conftest import register, login


def test_register_success(app, client):
    resp = register(client)
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']

    with app.app_context():
        u = User.query.filter_by(email='user@test.com').first()
        assert u is not None
        assert u.role == 'member'
        assert u.password_hash != 'Test@1234'
        assert u.check_password('Test@1234')


def test_register_duplicate_email(app, client):
    register(client)
    resp = register(client)
    assert resp.status_code == 400
    assert b'already exists' in resp.data


def test_register_weak_password_rejected(app, client):
    resp = client.post('/auth/register', data={
        'full_name': 'Weak Password User',
        'email': 'weak@test.com',
        'phone': '+919876543210',
        'password': 'short',
        'confirm': 'short',
    })
    assert resp.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email='weak@test.com').first() is None


def test_register_password_no_digit_rejected(app, client):
    resp = client.post('/auth/register', data={
        'full_name': 'No Digit User',
        'email': 'nodigit@test.com',
        'phone': '+919876543210',
        'password': 'abcdefgh',
        'confirm': 'abcdefgh',
    })
    assert resp.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email='nodigit@test.com').first() is None


def test_register_mismatched_confirm_rejected(app, client):
    resp = client.post('/auth/register', data={
        'full_name': 'Mismatch User',
        'email': 'mismatch@test.com',
        'phone': '+919876543210',
        'password': 'Test@1234',
        'confirm': 'Test@9999',
    })
    assert resp.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email='mismatch@test.com').first() is None


def test_login_success(app, client):
    register(client)
    resp = login(client)
    assert resp.status_code == 302


def test_login_wrong_password(app, client):
    register(client)
    resp = login(client, password='wrongpass')
    assert resp.status_code == 401
    assert b'Invalid email or password' in resp.data


def test_login_unknown_email(app, client):
    resp = login(client, email='nobody@test.com')
    assert resp.status_code == 401
    assert b'Invalid email or password' in resp.data


def test_login_inactive_account(app, client):
    register(client)
    with app.app_context():
        u = User.query.filter_by(email='user@test.com').first()
        u.is_active_account = False
        db.session.commit()
    resp = login(client)
    assert resp.status_code == 403
    assert b'disabled' in resp.data


def test_dashboard_requires_login(client):
    resp = client.get('/dashboard')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']


def test_dashboard_accessible_when_logged_in(client):
    register(client)
    login(client)
    resp = client.get('/dashboard')
    assert resp.status_code == 200


def test_logout(app, client):
    register(client)
    login(client)
    resp = client.get('/auth/logout')
    assert resp.status_code == 302

    resp2 = client.get('/dashboard')
    assert resp2.status_code == 302
    assert '/auth/login' in resp2.headers['Location']


def test_password_hashing(app, client):
    register(client)
    with app.app_context():
        u = User.query.filter_by(email='user@test.com').first()
        assert u.password_hash.startswith('pbkdf2:sha256:600000')
        assert u.check_password('Test@1234')
        assert not u.check_password('WrongPass')


def test_create_admin_cli(app, runner):
    result = runner.invoke(args=[
        'create-admin',
        '--email', 'admin@test.com',
        '--full-name', 'Admin User',
        '--phone', '+919876543210',
        '--password', 'Admin@1234',
    ])
    assert 'Admin created' in result.output

    with app.app_context():
        u = User.query.filter_by(email='admin@test.com').first()
        assert u is not None
        assert u.role == 'admin'


def test_list_users_cli(app, runner, client):
    register(client)
    result = runner.invoke(args=['list-users'])
    assert 'user@test.com' in result.output
    assert 'member' in result.output
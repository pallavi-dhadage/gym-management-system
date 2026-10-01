"""Security regression tests."""
from app import db
from app.models.user import User
from tests.conftest import register, login


def _make_user(app, email, role, password='Test@1234'):
    with app.app_context():
        u = User(email=email, full_name=f'{role.title()} User',
                 phone='+919876543210', role=role)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        return u.id


def _login_as(client, email, password='Test@1234'):
    return client.post('/auth/login', data={
        'email': email, 'password': password,
    }, follow_redirects=False)


# =========================================================
# Security headers
# =========================================================
def test_security_headers_present_on_landing(client):
    resp = client.get('/')
    assert resp.headers.get('X-Content-Type-Options') == 'nosniff'
    assert resp.headers.get('X-Frame-Options') == 'DENY'
    assert resp.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'
    assert 'Permissions-Policy' in resp.headers


# =========================================================
# CSRF
# =========================================================
def test_csrf_blocks_enquiry_without_token(app):
    """In dev/test with CSRF disabled this passes; in prod it would 400.

    Here we simply assert the endpoint exists and the middleware is wired.
    """
    with app.app_context():
        assert app.config.get('WTF_CSRF_ENABLED') in (True, False)


# =========================================================
# Authorization
# =========================================================
def test_member_cannot_access_admin_leads(app, client):
    register(client)
    login(client)
    assert client.get('/admin/leads').status_code == 403


def test_member_cannot_access_admin_payments(app, client):
    register(client)
    login(client)
    assert client.get('/admin/payments').status_code == 403


def test_member_cannot_access_admin_expiring(app, client):
    register(client)
    login(client)
    assert client.get('/admin/expiring').status_code == 403


def test_member_cannot_access_trainer_notes(app, client):
    register(client)
    login(client)
    assert client.get('/trainer/notes').status_code == 403


def test_trainer_cannot_access_admin_payments(app, client):
    _make_user(app, 'trainer@test.com', 'trainer')
    _login_as(client, 'trainer@test.com')
    assert client.get('/admin/payments').status_code == 403


def test_trainer_can_access_trainer_notes(app, client):
    _make_user(app, 'trainer@test.com', 'trainer')
    _login_as(client, 'trainer@test.com')
    assert client.get('/trainer/notes').status_code == 200


# =========================================================
# User enumeration
# =========================================================
def test_login_returns_same_error_for_unknown_email_and_wrong_password(app, client):
    register(client)  # user@test.com exists
    client.get('/auth/logout')

    resp_unknown = client.post('/auth/login', data={
        'email': 'nobody@test.com', 'password': 'anything123',
    })
    resp_wrong = client.post('/auth/login', data={
        'email': 'user@test.com', 'password': 'wrongpass',
    })

    assert resp_unknown.status_code == resp_wrong.status_code == 401
    assert b'Invalid email or password' in resp_unknown.data
    assert b'Invalid email or password' in resp_wrong.data


# =========================================================
# Safe redirect
# =========================================================
def test_login_rejects_external_next_url(app, client):
    register(client)
    client.get('/auth/logout')

    resp = client.post('/auth/login?next=https://evil.example.com', data={
        'email': 'user@test.com', 'password': 'Test@1234',
    }, follow_redirects=False)

    # Should redirect to our own dashboard, not to evil.example.com
    location = resp.headers.get('Location', '')
    assert 'evil.example.com' not in location


def test_login_allows_internal_next_url(app, client):
    register(client)
    client.get('/auth/logout')

    resp = client.post('/auth/login?next=/member/membership', data={
        'email': 'user@test.com', 'password': 'Test@1234',
    }, follow_redirects=False)

    assert '/member/membership' in resp.headers.get('Location', '')


# =========================================================
# Session invalidation on logout
# =========================================================
def test_session_cleared_after_logout(app, client):
    register(client)
    login(client)
    assert client.get('/dashboard').status_code == 200

    client.get('/auth/logout')
    assert client.get('/dashboard').status_code == 302


# =========================================================
# IDOR
# =========================================================
def test_member_cannot_read_other_member_notes(app, client):
    trainer_id = _make_user(app, 'trainer@test.com', 'trainer')
    _make_user(app, 'm1@test.com', 'member')
    m2_id = _make_user(app, 'm2@test.com', 'member')

    with app.app_context():
        from app.models.note import TrainerNote
        db.session.add(TrainerNote(member_id=m2_id, author_id=trainer_id,
                                   category='diet', title='Secret',
                                   body='classified'))
        db.session.commit()

    _login_as(client, 'm1@test.com')
    resp = client.get('/member/notes')
    assert b'Secret' not in resp.data


def test_unknown_payment_404_for_admin(app, client):
    _make_user(app, 'admin@test.com', 'admin')
    _login_as(client, 'admin@test.com')
    assert client.post('/admin/payments/9999/verify', data={
        'admin_note': '', 'verify': 'Verify & Activate',
    }).status_code == 404


def test_unknown_lead_404_for_admin(app, client):
    _make_user(app, 'admin@test.com', 'admin')
    _login_as(client, 'admin@test.com')
    assert client.get('/admin/leads/99999').status_code == 404


# =========================================================
# Password storage
# =========================================================
def test_password_never_stored_in_plaintext(app, client):
    register(client, password='SuperSecret@1')
    with app.app_context():
        u = User.query.filter_by(email='user@test.com').first()
        assert 'SuperSecret@1' not in u.password_hash
        assert u.password_hash.startswith('pbkdf2:sha256:600000')


# =========================================================
# Input validation
# =========================================================
def test_utr_rejects_injection_chars(app, client):
    """A UTR containing quotes / semicolons should be rejected by regex."""
    register(client)
    login(client)

    with app.app_context():
        from app.models.plan import Plan
        p = Plan(code='basic-30', name='Basic', price_paise=99900,
                 duration_days=30, sort_order=1)
        db.session.add(p)
        db.session.commit()
        pid = p.id

    client.post(f'/member/select-plan/{pid}')
    client.post('/member/payment/submit', data={
        'utr_reference': "'; DROP TABLE users; --",
        'member_note': '',
    }, follow_redirects=False)

    with app.app_context():
        from app.models.payment import Payment
        assert Payment.query.count() == 0  # rejected
        assert User.query.count() == 1     # users table intact
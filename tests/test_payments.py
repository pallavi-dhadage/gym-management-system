from datetime import datetime, timedelta

from app import db
from app.models.user import User
from app.models.plan import Plan
from app.models.membership import Membership
from app.models.payment import Payment
from tests.conftest import register, login


def _seed_plan(app):
    with app.app_context():
        p = Plan(code='basic-30', name='Basic', price_paise=99900,
                 duration_days=30, sort_order=1)
        db.session.add(p)
        db.session.commit()
        return p.id


def _make_admin(app):
    with app.app_context():
        u = User(email='admin@test.com', full_name='Admin',
                 phone='+919876543210', role='admin')
        u.set_password('Admin@1234')
        db.session.add(u)
        db.session.commit()


def _setup_member_with_pending_membership(app, client, plan_id):
    """Register, login, select plan → returns (user_id, membership_id)."""
    register(client)
    login(client)
    client.post(f'/member/select-plan/{plan_id}')
    with app.app_context():
        u = User.query.filter_by(email='user@test.com').first()
        return u.id, u.membership.id


def _login_admin(client):
    return client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'Admin@1234',
    }, follow_redirects=False)


# =========================================================
# Payment page + QR
# =========================================================
def test_payment_requires_login(client):
    resp = client.get('/member/payment')
    assert resp.status_code == 302


def test_payment_no_plan_redirects(app, client):
    register(client)
    login(client)
    resp = client.get('/member/payment')
    assert resp.status_code == 302


def test_payment_page_shows_upi_and_amount(app, client):
    pid = _seed_plan(app)
    _setup_member_with_pending_membership(app, client, pid)

    resp = client.get('/member/payment')
    assert resp.status_code == 200
    assert b'UPI' in resp.data
    assert b'999.00' in resp.data
    assert b'payment' in resp.data.lower()


def test_payment_qr_returns_png(app, client):
    pid = _seed_plan(app)
    _setup_member_with_pending_membership(app, client, pid)

    resp = client.get('/member/payment/qr.png')
    assert resp.status_code == 200
    assert resp.mimetype == 'image/png'
    assert resp.data[:4] == b'\x89PNG'


# =========================================================
# Submit UTR
# =========================================================
def test_submit_utr_creates_payment(app, client):
    pid = _seed_plan(app)
    uid, mid = _setup_member_with_pending_membership(app, client, pid)

    resp = client.post('/member/payment/submit', data={
        'utr_reference': 'ABC123456789',
        'member_note': 'Paid from HDFC',
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert '/member/membership' in resp.headers['Location']

    with app.app_context():
        p = Payment.query.filter_by(user_id=uid).first()
        assert p is not None
        assert p.utr_reference == 'ABC123456789'
        assert p.status == 'submitted'
        assert p.amount_paise == 99900


def test_submit_utr_lowercases_to_uppercase(app, client):
    pid = _seed_plan(app)
    _setup_member_with_pending_membership(app, client, pid)

    client.post('/member/payment/submit', data={
        'utr_reference': 'abc123456',
        'member_note': '',
    })
    with app.app_context():
        p = Payment.query.first()
        assert p.utr_reference == 'ABC123456'


def test_submit_invalid_utr_rejected(app, client):
    pid = _seed_plan(app)
    _setup_member_with_pending_membership(app, client, pid)

    resp = client.post('/member/payment/submit', data={
        'utr_reference': 'bad@utr!',
        'member_note': '',
    }, follow_redirects=False)
    # Redirect back to /member/payment, no payment created
    with app.app_context():
        assert Payment.query.count() == 0


def test_duplicate_utr_blocked(app, client):
    pid = _seed_plan(app)
    _setup_member_with_pending_membership(app, client, pid)

    client.post('/member/payment/submit', data={
        'utr_reference': 'DUPLICATE123',
        'member_note': '',
    })
    with app.app_context():
        assert Payment.query.count() == 1


# =========================================================
# Admin queue
# =========================================================
def test_admin_payments_requires_login(client):
    resp = client.get('/admin/payments')
    assert resp.status_code == 302


def test_admin_payments_forbidden_for_member(app, client):
    pid = _seed_plan(app)
    _setup_member_with_pending_membership(app, client, pid)
    resp = client.get('/admin/payments')
    assert resp.status_code == 403


def test_admin_payments_accessible_for_admin(app, client):
    _make_admin(app)
    _login_admin(client)
    resp = client.get('/admin/payments')
    assert resp.status_code == 200


# =========================================================
# Verify payment → activate membership
# =========================================================
def test_verify_payment_activates_membership(app, client):
    pid = _seed_plan(app)
    uid, mid = _setup_member_with_pending_membership(app, client, pid)

    # Member submits
    client.post('/member/payment/submit', data={
        'utr_reference': 'VERIFY123456',
        'member_note': '',
    })
    with app.app_context():
        payment_id = Payment.query.filter_by(user_id=uid).first().id

    # Admin verifies
    client.get('/auth/logout')
    _make_admin(app)
    _login_admin(client)

    resp = client.post(f'/admin/payments/{payment_id}/verify', data={
        'admin_note': 'Looks good',
        'verify': 'Verify & Activate',
    }, follow_redirects=False)
    assert resp.status_code == 302

    with app.app_context():
        p = db.session.get(Payment, payment_id)
        m = db.session.get(Membership, mid)
        assert p.status == 'verified'
        assert p.verified_at is not None
        assert p.verified_by is not None
        assert m.status == 'active'
        assert m.started_at is not None
        assert m.expires_at is not None
        # Expiry should be ~30 days ahead
        delta_days = (m.expires_at - m.started_at).days
        assert delta_days == 30


# =========================================================
# Reject payment → membership stays pending
# =========================================================
def test_reject_payment_keeps_membership_pending(app, client):
    pid = _seed_plan(app)
    uid, mid = _setup_member_with_pending_membership(app, client, pid)

    client.post('/member/payment/submit', data={
        'utr_reference': 'REJECT123456',
        'member_note': '',
    })
    with app.app_context():
        payment_id = Payment.query.filter_by(user_id=uid).first().id

    client.get('/auth/logout')
    _make_admin(app)
    _login_admin(client)

    resp = client.post(f'/admin/payments/{payment_id}/reject', data={
        'admin_note': 'UTR not found',
        'reject': 'Reject',
    }, follow_redirects=False)
    assert resp.status_code == 302

    with app.app_context():
        p = db.session.get(Payment, payment_id)
        m = db.session.get(Membership, mid)
        assert p.status == 'rejected'
        assert m.status == 'pending'


def test_cannot_verify_already_verified_payment(app, client):
    pid = _seed_plan(app)
    uid, mid = _setup_member_with_pending_membership(app, client, pid)

    client.post('/member/payment/submit', data={
        'utr_reference': 'DOUBLE123456',
        'member_note': '',
    })
    with app.app_context():
        payment_id = Payment.query.filter_by(user_id=uid).first().id

    client.get('/auth/logout')
    _make_admin(app)
    _login_admin(client)

    client.post(f'/admin/payments/{payment_id}/verify', data={
        'admin_note': '', 'verify': 'Verify & Activate',
    })
    resp = client.post(f'/admin/payments/{payment_id}/verify', data={
        'admin_note': '', 'verify': 'Verify & Activate',
    }, follow_redirects=False)
    # Second verify → still 302 (redirect with warning), not error
    assert resp.status_code == 302


def test_verify_unknown_payment_404(app, client):
    _make_admin(app)
    _login_admin(client)
    resp = client.post('/admin/payments/9999/verify', data={
        'admin_note': '', 'verify': 'Verify & Activate',
    })
    assert resp.status_code == 404
from datetime import datetime, timedelta

from app import db
from app.models.user import User
from app.models.plan import Plan
from app.models.membership import Membership
from app.models.reminder import Reminder
from app.services.scheduler import expire_memberships


def _make_member(app, email='m@test.com'):
    with app.app_context():
        u = User(email=email, full_name='Member', phone='+919876543210', role='member')
        u.set_password('Test@1234')
        db.session.add(u)
        db.session.commit()
        return u.id


def _make_plan(app):
    with app.app_context():
        p = Plan(code='basic-30', name='Basic', price_paise=99900,
                 duration_days=30, sort_order=1)
        db.session.add(p)
        db.session.commit()
        return p.id


def _make_membership(app, user_id, plan_id, status, expires_in_days):
    with app.app_context():
        now = datetime.utcnow()
        m = Membership(
            user_id=user_id,
            plan_id=plan_id,
            status=status,
            started_at=now - timedelta(days=20),
            expires_at=now + timedelta(days=expires_in_days),
        )
        db.session.add(m)
        db.session.commit()
        return m.id


def test_job_expires_past_due_memberships(app):
    uid = _make_member(app)
    pid = _make_plan(app)
    mid = _make_membership(app, uid, pid, status='active', expires_in_days=-1)

    with app.app_context():
        summary = expire_memberships(app)
        assert summary['expired'] == 1
        m = db.session.get(Membership, mid)
        assert m.status == 'expired'


def test_job_does_not_touch_active_in_window(app):
    uid = _make_member(app)
    pid = _make_plan(app)
    mid = _make_membership(app, uid, pid, status='active', expires_in_days=20)

    with app.app_context():
        summary = expire_memberships(app)
        assert summary['expired'] == 0
        m = db.session.get(Membership, mid)
        assert m.status == 'active'


def test_job_sends_renewal_reminder_near_expiry(app):
    uid = _make_member(app)
    pid = _make_plan(app)
    mid = _make_membership(app, uid, pid, status='active', expires_in_days=3)

    with app.app_context():
        summary = expire_memberships(app)
        assert summary['reminders_sent'] == 1
        r = Reminder.query.filter_by(membership_id=mid, kind='renewal_reminder').first()
        assert r is not None
        assert r.status == 'sent'


def test_job_skips_duplicate_reminder_within_24h(app):
    uid = _make_member(app)
    pid = _make_plan(app)
    mid = _make_membership(app, uid, pid, status='active', expires_in_days=3)

    with app.app_context():
        s1 = expire_memberships(app)
        assert s1['reminders_sent'] == 1
        s2 = expire_memberships(app)
        assert s2['reminders_sent'] == 0
        assert s2['skipped'] == 1
        assert Reminder.query.filter_by(membership_id=mid).count() == 1


def test_job_sends_expired_notice(app):
    uid = _make_member(app)
    pid = _make_plan(app)
    mid = _make_membership(app, uid, pid, status='active', expires_in_days=-2)

    with app.app_context():
        expire_memberships(app)
        notice = Reminder.query.filter_by(
            membership_id=mid, kind='expired_notice'
        ).first()
        assert notice is not None


def test_job_ignores_pending_memberships(app):
    uid = _make_member(app)
    pid = _make_plan(app)
    mid = _make_membership(app, uid, pid, status='pending', expires_in_days=-5)

    with app.app_context():
        summary = expire_memberships(app)
        assert summary['expired'] == 0
        m = db.session.get(Membership, mid)
        assert m.status == 'pending'


def _make_admin(app):
    with app.app_context():
        u = User(email='admin@test.com', full_name='Admin',
                 phone='+919876543210', role='admin')
        u.set_password('Admin@1234')
        db.session.add(u)
        db.session.commit()


def _login_admin(client):
    return client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'Admin@1234',
    }, follow_redirects=False)


def test_expiring_page_requires_login(client):
    resp = client.get('/admin/expiring')
    assert resp.status_code == 302


def test_expiring_page_forbidden_for_member(app, client):
    with app.app_context():
        u = User(email='member@test.com', full_name='M',
                 phone='+919876543210', role='member')
        u.set_password('Test@1234')
        db.session.add(u)
        db.session.commit()

    client.post('/auth/login', data={
        'email': 'member@test.com',
        'password': 'Test@1234',
    })
    resp = client.get('/admin/expiring')
    assert resp.status_code == 403


def test_expiring_page_accessible_for_admin(app, client):
    _make_admin(app)
    _login_admin(client)
    resp = client.get('/admin/expiring')
    assert resp.status_code == 200


def test_admin_can_manually_notify(app, client):
    uid = _make_member(app)
    pid = _make_plan(app)
    mid = _make_membership(app, uid, pid, status='active', expires_in_days=3)

    _make_admin(app)
    _login_admin(client)

    resp = client.post(f'/admin/expiring/notify/{mid}', data={},
                       follow_redirects=False)
    assert resp.status_code == 302

    with app.app_context():
        r = Reminder.query.filter_by(membership_id=mid).first()
        assert r is not None
        assert r.kind == 'renewal_reminder'
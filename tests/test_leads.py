from app import db
from app.models.lead import Lead
from app.models.user import User
from tests.conftest import register, login


def _submit_enquiry(client, email='lead@test.com',
                    name='Lead Person', phone='+919876543210',
                    message='I want a trial', website=''):
    return client.post('/enquiry', data={
        'full_name': name,
        'email': email,
        'phone': phone,
        'message': message,
        'website': website,
    }, follow_redirects=False)


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


# =========================================================
# Public enquiry form
# =========================================================
def test_enquiry_form_renders_on_landing(app, client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Free Trial Enquiry' in resp.data


def test_enquiry_valid_creates_lead(app, client):
    resp = _submit_enquiry(client)
    assert resp.status_code == 302

    with app.app_context():
        lead = Lead.query.filter_by(email='lead@test.com').first()
        assert lead is not None
        assert lead.status == 'new'
        assert lead.phone == '+919876543210'


def test_enquiry_invalid_email_no_lead(app, client):
    resp = _submit_enquiry(client, email='not-an-email')
    assert resp.status_code == 200
    with app.app_context():
        assert Lead.query.count() == 0


def test_enquiry_invalid_phone_no_lead(app, client):
    resp = _submit_enquiry(client, phone='abc')
    assert resp.status_code == 200
    with app.app_context():
        assert Lead.query.count() == 0


def test_enquiry_honeypot_blocks_bot(app, client):
    resp = _submit_enquiry(client, email='bot@test.com', website='http://spam.example')
    assert resp.status_code == 302
    with app.app_context():
        assert Lead.query.filter_by(email='bot@test.com').first() is None


# =========================================================
# Admin-only access
# =========================================================
def test_admin_leads_requires_login(client):
    resp = client.get('/admin/leads')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']


def test_admin_leads_forbidden_for_member(app, client):
    register(client)
    login(client)
    resp = client.get('/admin/leads')
    assert resp.status_code == 403


def test_admin_leads_accessible_for_admin(app, client):
    _make_admin(app)
    _login_admin(client)
    resp = client.get('/admin/leads')
    assert resp.status_code == 200


def test_admin_lead_detail_404_for_unknown(app, client):
    _make_admin(app)
    _login_admin(client)
    resp = client.get('/admin/leads/9999')
    assert resp.status_code == 404


# =========================================================
# Admin updates status
# =========================================================
def test_admin_updates_lead_status(app, client):
    _submit_enquiry(client)

    _make_admin(app)
    _login_admin(client)

    with app.app_context():
        lead_id = Lead.query.filter_by(email='lead@test.com').first().id

    resp = client.post(f'/admin/leads/{lead_id}', data={
        'status': 'contacted',
        'notes': 'Called on Monday',
    }, follow_redirects=False)
    assert resp.status_code == 302

    with app.app_context():
        lead = db.session.get(Lead, lead_id)
        assert lead.status == 'contacted'
        assert lead.notes == 'Called on Monday'
        assert lead.handled_by is not None
        assert lead.handled_at is not None


def test_admin_cannot_set_invalid_status(app, client):
    _submit_enquiry(client)

    _make_admin(app)
    _login_admin(client)

    with app.app_context():
        lead_id = Lead.query.filter_by(email='lead@test.com').first().id

    resp = client.post(f'/admin/leads/{lead_id}', data={
        'status': 'hacked',
    }, follow_redirects=False)
    assert resp.status_code == 200

    with app.app_context():
        lead = db.session.get(Lead, lead_id)
        assert lead.status == 'new'
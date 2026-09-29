from app import db
from app.models.user import User
from app.models.note import TrainerNote
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
        'email': email,
        'password': password,
    }, follow_redirects=False)


def test_notes_list_requires_login(client):
    resp = client.get('/trainer/notes')
    assert resp.status_code == 302


def test_notes_list_forbidden_for_member(app, client):
    register(client)
    login(client)
    resp = client.get('/trainer/notes')
    assert resp.status_code == 403


def test_notes_list_accessible_for_trainer(app, client):
    _make_user(app, 'trainer@test.com', 'trainer')
    _login_as(client, 'trainer@test.com')
    resp = client.get('/trainer/notes')
    assert resp.status_code == 200


def test_notes_list_accessible_for_admin(app, client):
    _make_user(app, 'admin@test.com', 'admin')
    _login_as(client, 'admin@test.com')
    resp = client.get('/trainer/notes')
    assert resp.status_code == 200


def test_create_note_as_trainer(app, client):
    _make_user(app, 'trainer@test.com', 'trainer')
    member_id = _make_user(app, 'member@test.com', 'member')

    _login_as(client, 'trainer@test.com')

    resp = client.post('/trainer/notes/new', data={
        'member_id': member_id,
        'category': 'workout',
        'title': 'Upper body day',
        'body': '3x10 bench press',
    }, follow_redirects=False)
    assert resp.status_code == 302

    with app.app_context():
        n = TrainerNote.query.first()
        assert n is not None
        assert n.member_id == member_id
        assert n.category == 'workout'
        assert n.title == 'Upper body day'


def test_create_note_forbidden_for_member(app, client):
    _make_user(app, 'trainer@test.com', 'trainer')
    member_id = _make_user(app, 'member@test.com', 'member')

    _login_as(client, 'member@test.com')
    resp = client.post('/trainer/notes/new', data={
        'member_id': member_id,
        'category': 'workout',
        'title': 'x',
        'body': 'y',
    }, follow_redirects=False)
    assert resp.status_code == 403


def test_create_note_invalid_member_rejected(app, client):
    _make_user(app, 'trainer@test.com', 'trainer')
    _make_user(app, 'admin@test.com', 'admin')

    _login_as(client, 'trainer@test.com')
    with app.app_context():
        admin_id = User.query.filter_by(email='admin@test.com').first().id

    client.post('/trainer/notes/new', data={
        'member_id': admin_id,
        'category': 'workout',
        'title': 'test',
        'body': 'test',
    })
    with app.app_context():
        assert TrainerNote.query.count() == 0


def test_member_sees_own_notes(app, client):
    trainer_id = _make_user(app, 'trainer@test.com', 'trainer')
    member_id = _make_user(app, 'member@test.com', 'member')

    with app.app_context():
        db.session.add(TrainerNote(member_id=member_id, author_id=trainer_id,
                                   category='diet', title='Drink water',
                                   body='2L per day'))
        db.session.commit()

    _login_as(client, 'member@test.com')
    resp = client.get('/member/notes')
    assert resp.status_code == 200
    assert b'Drink water' in resp.data


def test_member_does_not_see_other_members_notes(app, client):
    trainer_id = _make_user(app, 'trainer@test.com', 'trainer')
    _make_user(app, 'm1@test.com', 'member')
    m2 = _make_user(app, 'm2@test.com', 'member')

    with app.app_context():
        db.session.add(TrainerNote(member_id=m2, author_id=trainer_id,
                                   category='workout', title='Secret plan',
                                   body='for m2 only'))
        db.session.commit()

    _login_as(client, 'm1@test.com')
    resp = client.get('/member/notes')
    assert resp.status_code == 200
    assert b'Secret plan' not in resp.data


def test_trainer_can_edit_note(app, client):
    trainer_id = _make_user(app, 'trainer@test.com', 'trainer')
    member_id = _make_user(app, 'member@test.com', 'member')

    with app.app_context():
        n = TrainerNote(member_id=member_id, author_id=trainer_id,
                        category='general', title='Old', body='Old body')
        db.session.add(n)
        db.session.commit()
        note_id = n.id

    _login_as(client, 'trainer@test.com')
    resp = client.post(f'/trainer/notes/{note_id}', data={
        'member_id': member_id,
        'category': 'workout',
        'title': 'New title',
        'body': 'New body',
    }, follow_redirects=False)
    assert resp.status_code == 302

    with app.app_context():
        n = db.session.get(TrainerNote, note_id)
        assert n.title == 'New title'
        assert n.category == 'workout'


def test_trainer_can_delete_note(app, client):
    trainer_id = _make_user(app, 'trainer@test.com', 'trainer')
    member_id = _make_user(app, 'member@test.com', 'member')

    with app.app_context():
        n = TrainerNote(member_id=member_id, author_id=trainer_id,
                        category='general', title='Bye', body='x')
        db.session.add(n)
        db.session.commit()
        note_id = n.id

    _login_as(client, 'trainer@test.com')
    resp = client.post(f'/trainer/notes/{note_id}/delete', data={},
                       follow_redirects=False)
    assert resp.status_code == 302

    with app.app_context():
        assert db.session.get(TrainerNote, note_id) is None


def test_edit_unknown_note_404(app, client):
    _make_user(app, 'trainer@test.com', 'trainer')
    _login_as(client, 'trainer@test.com')
    resp = client.get('/trainer/notes/9999')
    assert resp.status_code == 404
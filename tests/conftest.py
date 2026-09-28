import os
import pytest

os.environ['FLASK_ENV'] = 'testing'

from app import create_app, db as _db
from config import TestingConfig


@pytest.fixture(scope='function')
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def register(client, email='user@test.com', password='Test@1234',
             full_name='Test User', phone='+919876543210'):
    return client.post('/auth/register', data={
        'full_name': full_name,
        'email': email,
        'phone': phone,
        'password': password,
        'confirm': password,
        'csrf_token': 'test-token',
    }, follow_redirects=False)


def login(client, email='user@test.com', password='Test@1234'):
    return client.post('/auth/login', data={
        'email': email,
        'password': password,
        'csrf_token': 'test-token',
    }, follow_redirects=False)

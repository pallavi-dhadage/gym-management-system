from app import create_app
from config import TestingConfig

app = create_app(TestingConfig)

with app.test_request_context(
    method='POST',
    data={
        'full_name': 'Weak Password User',
        'email': 'weak@test.com',
        'phone': '+919876543210',
        'password': 'short',
        'confirm': 'short',
    },
):
    from app.routes.auth import RegisterForm
    f = RegisterForm()
    valid = f.validate_on_submit()
    print('valid:', valid)
    print('errors:', f.errors)
    print('password.errors:', f.password.errors)
    print('email.errors:', f.email.errors)
    print('phone.errors:', f.phone.errors)
    print('full_name.errors:', f.full_name.errors)
    print('confirm.errors:', f.confirm.errors)

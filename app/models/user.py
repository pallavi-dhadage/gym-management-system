from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='member', index=True)
    is_active_account = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    # One-to-one: the member's membership
    membership = db.relationship(
        'Membership',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan',
        foreign_keys='Membership.user_id',
    )

    # ----- Password handling -----
    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(
            raw_password, method='pbkdf2:sha256:600000'
        )

    def check_password(self, raw_password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw_password)

    # ----- Flask-Login overrides -----
    @property
    def is_active(self) -> bool:
        return bool(self.is_active_account)

    # ----- Role helpers -----
    def has_role(self, *roles: str) -> bool:
        return self.role in roles

    def __repr__(self) -> str:
        return f'<User {self.email} role={self.role}>'
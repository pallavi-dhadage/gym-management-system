from datetime import datetime

from app import db


class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(40), default='landing_page', nullable=False)

    status = db.Column(
        db.String(20),
        default='new',
        nullable=False,
        index=True,
    )

    handled_by_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )
    handled_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

    handled_by = db.relationship('User', foreign_keys=[handled_by_id], lazy='joined')

    STATUS_CHOICES = ('new', 'contacted', 'converted', 'rejected')

    def __repr__(self) -> str:
        return f'<Lead {self.id} {self.email} status={self.status}>'
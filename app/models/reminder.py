from datetime import datetime

from app import db


class Reminder(db.Model):
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)

    membership_id = db.Column(
        db.Integer,
        db.ForeignKey('memberships.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    kind = db.Column(db.String(30), nullable=False, index=True)

    status = db.Column(
        db.String(20), default='queued', nullable=False, index=True
    )

    message = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    sent_at = db.Column(db.DateTime, nullable=True)

    membership = db.relationship('Membership', lazy='joined')

    KIND_CHOICES = ('renewal_reminder', 'expired_notice')

    def __repr__(self) -> str:
        return f'<Reminder {self.id} membership={self.membership_id} kind={self.kind} status={self.status}>'
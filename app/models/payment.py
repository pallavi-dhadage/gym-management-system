from datetime import datetime

from app import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    membership_id = db.Column(
        db.Integer,
        db.ForeignKey('memberships.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    # Snapshot of the amount at the time of submission (paise)
    amount_paise = db.Column(db.Integer, nullable=False)

    # Member-submitted UTR / reference number
    utr_reference = db.Column(db.String(60), nullable=False, unique=True, index=True)

    # Optional member note ("paid from HDFC at 3:40 PM")
    member_note = db.Column(db.String(255), nullable=True)

    # submitted → verified | rejected
    status = db.Column(
        db.String(20), default='submitted', nullable=False, index=True
    )

    # Admin verification
    verified_by_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )
    verified_at = db.Column(db.DateTime, nullable=True)
    admin_note = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship('User', foreign_keys=[user_id], lazy='joined')
    membership = db.relationship('Membership', foreign_keys=[membership_id], lazy='joined')
    verified_by = db.relationship('User', foreign_keys=[verified_by_id], lazy='joined')

    STATUS_CHOICES = ('submitted', 'verified', 'rejected')

    @property
    def amount_rupees(self) -> float:
        return self.amount_paise / 100.0

    def __repr__(self) -> str:
        return f'<Payment {self.id} user={self.user_id} utr={self.utr_reference} status={self.status}>'
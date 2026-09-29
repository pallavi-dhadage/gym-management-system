from datetime import datetime, timedelta

from app import db


class Membership(db.Model):
    __tablename__ = 'memberships'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True,
    )
    plan_id = db.Column(
        db.Integer,
        db.ForeignKey('plans.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
    )

    status = db.Column(
        db.String(20), default='pending', nullable=False, index=True
    )

    started_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True, index=True)

    activated_by_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )
    activated_at = db.Column(db.DateTime, nullable=True)

    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancel_reason = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = db.relationship(
        'User',
        back_populates='membership',
        foreign_keys=[user_id],
    )
    plan = db.relationship('Plan', back_populates='memberships', lazy='joined')
    activated_by = db.relationship(
        'User', foreign_keys=[activated_by_id], lazy='joined'
    )

    STATUS_CHOICES = ('pending', 'active', 'expired', 'cancelled')
    EDITABLE_STATUSES = ('pending',)

    def is_active_now(self) -> bool:
        if self.status != 'active' or self.expires_at is None:
            return False
        return self.expires_at > datetime.utcnow()

    def days_remaining(self) -> int:
        if self.expires_at is None:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(delta.days, 0)

    def can_change_plan(self) -> bool:
        return self.status in self.EDITABLE_STATUSES

    def compute_expiry(self, from_dt: datetime = None) -> datetime:
        base = from_dt or datetime.utcnow()
        return base + timedelta(days=self.plan.duration_days)

    def __repr__(self) -> str:
        return f'<Membership user={self.user_id} plan={self.plan_id} status={self.status}>'
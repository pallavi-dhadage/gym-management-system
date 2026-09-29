from datetime import datetime

from app import db


class Plan(db.Model):
    __tablename__ = 'plans'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Store price in paise (integer) to avoid float rounding issues
    price_paise = db.Column(db.Integer, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)

    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    memberships = db.relationship('Membership', back_populates='plan', lazy='dynamic')

    @property
    def price_rupees(self) -> float:
        return self.price_paise / 100.0

    def __repr__(self) -> str:
        return f'<Plan {self.code} ₹{self.price_rupees:.2f}>'
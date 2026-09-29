from datetime import datetime

from app import db


class TrainerNote(db.Model):
    __tablename__ = 'trainer_notes'

    id = db.Column(db.Integer, primary_key=True)

    member_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    author_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )

    # workout | diet | general
    category = db.Column(
        db.String(20), default='general', nullable=False, index=True
    )

    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    member = db.relationship('User', foreign_keys=[member_id], lazy='joined')
    author = db.relationship('User', foreign_keys=[author_id], lazy='joined')

    CATEGORY_CHOICES = ('workout', 'diet', 'general')

    def __repr__(self) -> str:
        return f'<TrainerNote {self.id} member={self.member_id} category={self.category}>'
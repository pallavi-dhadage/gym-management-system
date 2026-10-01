"""
Notification service — v1 stub.
"""
from datetime import datetime

from flask import current_app

from app import db
from app.models.reminder import Reminder
from app.models.membership import Membership
from app.utils.logger import get_audit_logger

audit = get_audit_logger()


def send_renewal_reminder(membership: Membership) -> Reminder:
    """Create a renewal reminder for a membership expiring soon."""
    days = membership.days_remaining() if membership.expires_at else 0
    plan_name = membership.plan.name if membership.plan else 'membership'
    message = (
        f'Your {plan_name} expires in {days} day(s) on '
        f'{membership.expires_at.strftime("%Y-%m-%d") if membership.expires_at else "?"}. '
        f'Please renew to keep your access.'
    )

    reminder = Reminder(
        membership_id=membership.id,
        kind='renewal_reminder',
        status='sent',
        message=message,
        sent_at=datetime.utcnow(),
    )
    db.session.add(reminder)
    db.session.commit()

    audit.info(
        'REMINDER_SENT membership_id=%s user_id=%s kind=renewal_reminder days_left=%s',
        membership.id, membership.user_id, days,
    )
    current_app.logger.info('Renewal reminder for membership %s', membership.id)
    return reminder


def send_expiry_notice(membership: Membership) -> Reminder:
    """Log an expiry notice (membership is now expired)."""
    plan_name = membership.plan.name if membership.plan else 'membership'
    message = f'Your {plan_name} has expired. Renew to continue training.'

    reminder = Reminder(
        membership_id=membership.id,
        kind='expired_notice',
        status='sent',
        message=message,
        sent_at=datetime.utcnow(),
    )
    db.session.add(reminder)
    db.session.commit()

    audit.info(
        'REMINDER_SENT membership_id=%s user_id=%s kind=expired_notice',
        membership.id, membership.user_id,
    )
    return reminder
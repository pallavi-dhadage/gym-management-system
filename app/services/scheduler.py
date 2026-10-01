"""
APScheduler-based daily job runner.
"""
from datetime import datetime, timedelta
import os

from apscheduler.schedulers.background import BackgroundScheduler

from app import db
from app.models.membership import Membership
from app.models.reminder import Reminder
from app.services.notifications import send_renewal_reminder, send_expiry_notice
from app.utils.logger import get_audit_logger

audit = get_audit_logger()

_scheduler = None


def expire_memberships(app) -> dict:
    """Daily job: expire overdue memberships + send renewal reminders."""
    with app.app_context():
        now = datetime.utcnow()
        summary = {'expired': 0, 'notices_sent': 0, 'reminders_sent': 0, 'skipped': 0}

        expired = (
            Membership.query
            .filter(Membership.status == 'active')
            .filter(Membership.expires_at.isnot(None))
            .filter(Membership.expires_at < now)
            .all()
        )
        for m in expired:
            m.status = 'expired'
            summary['expired'] += 1
            try:
                send_expiry_notice(m)
                summary['notices_sent'] += 1
            except Exception:
                app.logger.exception('EXPIRY_NOTICE_FAILED membership_id=%s', m.id)

        if expired:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                app.logger.exception('EXPIRE_COMMIT_FAILED')

        window_days = int(app.config.get('MEMBERSHIP_REMINDER_DAYS', 7))
        horizon = now + timedelta(days=window_days)

        expiring_soon = (
            Membership.query
            .filter(Membership.status == 'active')
            .filter(Membership.expires_at.isnot(None))
            .filter(Membership.expires_at >= now)
            .filter(Membership.expires_at <= horizon)
            .all()
        )

        for m in expiring_soon:
            already = (
                Reminder.query
                .filter_by(membership_id=m.id, kind='renewal_reminder')
                .filter(Reminder.sent_at >= now - timedelta(hours=24))
                .first()
            )
            if already:
                summary['skipped'] += 1
                continue

            try:
                send_renewal_reminder(m)
                summary['reminders_sent'] += 1
            except Exception:
                app.logger.exception('REMINDER_FAILED membership_id=%s', m.id)

        audit.info(
            'DAILY_JOB_RUN expired=%s notices=%s reminders=%s skipped=%s',
            summary['expired'], summary['notices_sent'],
            summary['reminders_sent'], summary['skipped'],
        )
        return summary


def start_scheduler(app):
    """Start the background scheduler (idempotent, debug-reloader safe)."""
    global _scheduler

    if not app.config.get('SCHEDULER_ENABLED', True):
        app.logger.info('Scheduler disabled by config')
        return None

    if app.debug and os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        app.logger.info('Scheduler skipped in reloader parent')
        return None

    if _scheduler is not None and _scheduler.running:
        return _scheduler

    sched = BackgroundScheduler(daemon=True, timezone='UTC')
    hour = int(app.config.get('SCHEDULER_HOUR', 2))

    sched.add_job(
        func=lambda: expire_memberships(app),
        trigger='cron',
        hour=hour,
        minute=0,
        id='daily_expiry_check',
        replace_existing=True,
        misfire_grace_time=3600,
    )
    sched.start()
    _scheduler = sched

    app.logger.info('Scheduler started — daily expiry check at %02d:00 UTC', hour)
    return sched


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        _scheduler = None
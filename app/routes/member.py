from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, abort, current_app
)
from flask_login import login_required, current_user

from app import db
from app.models.plan import Plan
from app.models.membership import Membership
from app.utils.logger import get_audit_logger

member_bp = Blueprint('member', __name__)
audit = get_audit_logger()


@member_bp.route('/plans')
@login_required
def plans():
    available = (
        Plan.query
        .filter_by(is_active=True)
        .order_by(Plan.sort_order.asc(), Plan.price_paise.asc())
        .all()
    )
    return render_template(
        'member/plans.html',
        plans=available,
        membership=current_user.membership,
    )


@member_bp.route('/select-plan/<int:plan_id>', methods=['POST'])
@login_required
def select_plan(plan_id: int):
    plan = db.session.get(Plan, plan_id)
    if plan is None or not plan.is_active:
        abort(404)

    membership = current_user.membership

    if membership is None:
        membership = Membership(
            user_id=current_user.id,
            plan_id=plan.id,
            status='pending',
        )
        db.session.add(membership)
        audit.info('MEMBERSHIP_CREATED user_id=%s plan=%s',
                   current_user.id, plan.code)
        flash(f'Plan "{plan.name}" selected. Please complete payment to activate.',
              'success')
    else:
        if not membership.can_change_plan():
            audit.warning('MEMBERSHIP_CHANGE_DENIED user_id=%s status=%s',
                          current_user.id, membership.status)
            flash('Your membership is not editable in its current state.', 'danger')
            return redirect(url_for('member.membership'))

        old_plan_id = membership.plan_id
        membership.plan_id = plan.id
        audit.info('MEMBERSHIP_PLAN_CHANGED user_id=%s old_plan=%s new_plan=%s',
                   current_user.id, old_plan_id, plan.code)
        flash(f'Plan changed to "{plan.name}".', 'success')

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception('MEMBERSHIP_SAVE_FAILED user_id=%s', current_user.id)
        flash('Could not save your plan. Please try again.', 'danger')
        return redirect(url_for('member.plans'))

    return redirect(url_for('member.membership'))


@member_bp.route('/membership')
@login_required
def membership():
    return render_template('member/membership.html', membership=current_user.membership)
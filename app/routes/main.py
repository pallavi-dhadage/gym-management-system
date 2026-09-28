from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    current_app.logger.info('Landing page visited')
    return render_template('index.html')


@main_bp.route('/enquiry', methods=['GET'])
def enquiry():
    # full implementation in Phase 3
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

from flask import Blueprint, render_template, current_app
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    current_app.logger.info('Landing page visited')
    return render_template('index.html', now_year=datetime.utcnow().year)


@main_bp.route('/enquiry', methods=['GET'])
def enquiry():
    # full implementation in Phase 3
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
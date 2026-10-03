import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress

from config import get_config
from app.utils.logger import configure_logging
from app.utils.errors import register_error_handlers
from app.utils.security import register_security_headers

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
compress = Compress()


def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class or get_config())

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['LOG_DIR'], exist_ok=True)

    configure_logging(app)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    compress.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = 'strong'

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.member import member_bp
    from app.routes.trainer import trainer_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(member_bp, url_prefix='/member')
    app.register_blueprint(trainer_bp, url_prefix='/trainer')

    register_error_handlers(app)
    register_security_headers(app)

    from app.cli import register_cli
    register_cli(app)

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {'now_year': datetime.utcnow().year}

    if not app.config.get('TESTING'):
        from app.services.scheduler import start_scheduler
        start_scheduler(app)

    app.logger.info('Application factory completed. Env=%s', app.config.get('ENV', 'development'))
    return app


__all__ = ['create_app', 'db', 'login_manager', 'csrf', 'limiter', 'compress']
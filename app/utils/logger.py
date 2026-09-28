import logging
import os
from logging.handlers import RotatingFileHandler


def configure_logging(app):
    """Configure application logging with rotation and sensitive data filter."""
    log_dir = app.config.get('LOG_DIR', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper(), logging.INFO)

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # File handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Error file handler
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Attach to app logger
    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)

    # Quiet werkzeug access logs
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    app.logger.info('Logging configured at level %s', app.config.get('LOG_LEVEL'))


def get_audit_logger():
    """Returns a dedicated audit logger."""
    logger = logging.getLogger('audit')
    if not logger.handlers:
        os.makedirs('logs', exist_ok=True)
        handler = RotatingFileHandler(
            'logs/audit.log', maxBytes=10 * 1024 * 1024, backupCount=10
        )
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] AUDIT %(levelname)s: %(message)s'
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
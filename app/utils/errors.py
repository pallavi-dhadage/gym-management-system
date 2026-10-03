from flask import render_template, request, jsonify, current_app
from werkzeug.exceptions import HTTPException


def _wants_json() -> bool:
    return request.accept_mimetypes.best == 'application/json'


def _log_security_event(status_code: int, error_type: str):
    """Log security events with enhanced details."""
    from app.utils.security import _client_ip
    
    ip = _client_ip()
    ua = request.headers.get('User-Agent', 'unknown')[:100]
    method = request.method
    path = request.path
    referer = request.headers.get('Referer', 'none')
    
    current_app.logger.warning(
        f'SECURITY {status_code} {error_type} method={method} path={path} '
        f'ip={ip} ua="{ua}" referer={referer}'
    )


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        _log_security_event(400, 'bad_request')
        if _wants_json():
            return jsonify(error='Bad request', status=400), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        _log_security_event(401, 'unauthorized')
        if _wants_json():
            return jsonify(error='Unauthorized', status=401), 401
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden(e):
        _log_security_event(403, 'forbidden')
        if _wants_json():
            return jsonify(error='Forbidden', status=403), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        # Don't log 404s as security events (too noisy)
        if _wants_json():
            return jsonify(error='Not found', status=404), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(429)
    def rate_limited(e):
        _log_security_event(429, 'rate_limit')
        if _wants_json():
            return jsonify(error='Too many requests', status=429, 
                         message='Please try again later'), 429
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception(f'500 internal_error method={request.method} path={request.path}')
        if _wants_json():
            return jsonify(error='Internal server error', status=500), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        if isinstance(e, HTTPException):
            return e
        
        # Log unhandled exceptions with full context
        from app.utils.security import _client_ip
        ip = _client_ip()
        app.logger.exception(
            f'Unhandled exception: {e.__class__.__name__}: {str(e)} '
            f'method={request.method} path={request.path} ip={ip}'
        )
        
        if _wants_json():
            return jsonify(error='Internal server error', status=500), 500
        return render_template('errors/500.html'), 500
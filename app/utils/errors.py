from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """Register safe error handlers."""

    @app.errorhandler(400)
    def bad_request(e):
        app.logger.warning('400 Bad Request: %s %s', request.method, request.path)
        if request.accept_mimetypes.best == 'application/json':
            return jsonify(error='Bad request'), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if request.accept_mimetypes.best == 'application/json':
            return jsonify(error='Unauthorized'), 401
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden(e):
        app.logger.warning('403 Forbidden: %s %s', request.method, request.path)
        if request.accept_mimetypes.best == 'application/json':
            return jsonify(error='Forbidden'), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        if request.accept_mimetypes.best == 'application/json':
            return jsonify(error='Not found'), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(429)
    def rate_limited(e):
        app.logger.warning('429 Rate limit hit: %s %s', request.method, request.path)
        if request.accept_mimetypes.best == 'application/json':
            return jsonify(error='Too many requests'), 429
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception('500 Internal Server Error: %s %s', request.method, request.path)
        if request.accept_mimetypes.best == 'application/json':
            return jsonify(error='Internal server error'), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        if isinstance(e, HTTPException):
            return e
        app.logger.exception('Unhandled exception: %s', e)
        if request.accept_mimetypes.best == 'application/json':
            return jsonify(error='Internal server error'), 500
        return render_template('errors/500.html'), 500
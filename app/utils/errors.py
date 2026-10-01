from flask import render_template, request, jsonify, current_app
from werkzeug.exceptions import HTTPException


def _wants_json() -> bool:
    return request.accept_mimetypes.best == 'application/json'


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        app.logger.warning('SECURITY 400 bad_request %s %s ip=%s',
                           request.method, request.path, request.remote_addr)
        if _wants_json():
            return jsonify(error='Bad request'), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        app.logger.warning('SECURITY 401 unauthorized %s %s ip=%s',
                           request.method, request.path, request.remote_addr)
        if _wants_json():
            return jsonify(error='Unauthorized'), 401
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden(e):
        app.logger.warning('SECURITY 403 forbidden %s %s ip=%s',
                           request.method, request.path, request.remote_addr)
        if _wants_json():
            return jsonify(error='Forbidden'), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        if _wants_json():
            return jsonify(error='Not found'), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(429)
    def rate_limited(e):
        app.logger.warning('SECURITY 429 rate_limit %s %s ip=%s',
                           request.method, request.path, request.remote_addr)
        if _wants_json():
            return jsonify(error='Too many requests'), 429
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception('500 internal_error %s %s',
                             request.method, request.path)
        if _wants_json():
            return jsonify(error='Internal server error'), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        if isinstance(e, HTTPException):
            return e
        app.logger.exception('Unhandled exception: %s', e)
        if _wants_json():
            return jsonify(error='Internal server error'), 500
        return render_template('errors/500.html'), 500
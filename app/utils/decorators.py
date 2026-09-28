from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user


def role_required(*allowed_roles: str):
    """
    Decorator: restrict a route to specific roles.
    Usage: @role_required('admin', 'trainer')
    Must be applied AFTER @login_required.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to continue.', 'warning')
                return redirect(url_for('auth.login', next=request.path))
            if current_user.role not in allowed_roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator

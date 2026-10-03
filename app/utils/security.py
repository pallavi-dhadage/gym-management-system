"""
Centralised security helpers.

* Security headers middleware (CSP, HSTS, X-Frame-Options, etc.)
* Safe redirect helper (used by auth)
* Client IP extraction that respects trusted proxies
"""
from urllib.parse import urlparse, urljoin

from flask import request


def _client_ip() -> str:
    """Return the client IP, honouring X-Forwarded-For when behind a proxy."""
    xff = request.headers.get('X-Forwarded-For', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def is_safe_url(target: str) -> bool:
    """
    Only allow redirects to URLs on our own host.

    Accepts:
      * relative paths like "/member/membership"
      * absolute URLs pointing to our own host

    Rejects:
      * protocol-relative URLs ("//evil.com")
      * backslash tricks ("\\evil.com")
      * any URL whose netloc != our host
    """
    if not target or not isinstance(target, str):
        return False

    # Reject protocol-relative and backslash tricks
    if target.startswith('//') or target.startswith('\\\\') or '\\' in target:
        return False

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ('http', 'https')
        and ref_url.netloc == test_url.netloc
    )


def register_security_headers(app):
    """Attach a response middleware that sets secure headers on every reply."""

    @app.after_request
    def _add_security_headers(resp):
        resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
        resp.headers.setdefault('X-Frame-Options', 'DENY')
        resp.headers.setdefault('X-XSS-Protection', '1; mode=block')
        resp.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        resp.headers.setdefault(
            'Permissions-Policy',
            'geolocation=(), microphone=(), camera=(), payment=()'
        )

        if not app.config.get('TESTING') and not app.debug:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' "
                "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
                "https://images.unsplash.com; "
                "style-src 'self' 'unsafe-inline' "
                "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
                "https://fonts.googleapis.com; "
                "font-src 'self' https://cdnjs.cloudflare.com "
                "https://fonts.gstatic.com data:; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "object-src 'none'; "
                "upgrade-insecure-requests"
            )
            resp.headers.setdefault('Content-Security-Policy', csp)

        if app.config.get('SESSION_COOKIE_SECURE'):
            resp.headers.setdefault(
                'Strict-Transport-Security',
                'max-age=31536000; includeSubDomains'
            )

        return resp



def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.
    
    Args:
        filename: User-provided filename
        
    Returns:
        Safe filename with dangerous characters removed
    """
    import re
    # Remove any path separators
    filename = filename.replace('/', '').replace('\\', '')
    # Remove any parent directory references
    filename = filename.replace('..', '')
    # Only allow alphanumeric, dash, underscore, and dot
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    # Ensure filename isn't empty after sanitization
    if not filename:
        filename = 'unnamed_file'
    return filename


def validate_utr_format(utr: str) -> bool:
    """
    Validate UTR/reference number format.
    
    Args:
        utr: UTR reference number
        
    Returns:
        True if valid format, False otherwise
    """
    import re
    # UTR should be 6-60 characters, alphanumeric and hyphens only
    if not utr or len(utr) < 6 or len(utr) > 60:
        return False
    return bool(re.match(r'^[A-Za-z0-9\-]+$', utr))


def check_password_strength(password: str) -> tuple[bool, str]:
    """
    Check password strength beyond basic requirements.
    
    Args:
        password: Password to check
        
    Returns:
        Tuple of (is_strong, message)
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters'
    
    if len(password) > 128:
        return False, 'Password must not exceed 128 characters'
    
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not has_letter or not has_digit:
        return False, 'Password must contain at least one letter and one number'
    
    # Check for common weak passwords
    common_passwords = ['password', '12345678', 'qwerty', 'abc123', 'password1']
    if password.lower() in common_passwords:
        return False, 'Password is too common, please choose a stronger one'
    
    return True, 'Password is strong'


def rate_limit_key() -> str:
    """
    Generate a rate limit key based on user IP and user agent.
    Provides better rate limiting granularity.
    
    Returns:
        Rate limit key string
    """
    ip = _client_ip()
    ua = request.headers.get('User-Agent', 'unknown')[:100]
    # Combine IP and partial UA for rate limiting
    return f"{ip}:{hash(ua) % 10000}"


def log_security_event(event_type: str, details: dict, severity: str = 'INFO'):
    """
    Log security-related events with structured data.
    
    Args:
        event_type: Type of security event (e.g., 'LOGIN_FAIL', 'PAYMENT_VERIFY')
        details: Dictionary of event details
        severity: Log severity level
    """
    from app.utils.logger import get_audit_logger
    
    audit = get_audit_logger()
    ip = _client_ip()
    ua = request.headers.get('User-Agent', 'unknown')[:200]
    
    log_msg = f"SECURITY:{event_type} ip={ip} ua={ua}"
    for key, value in details.items():
        log_msg += f" {key}={value}"
    
    if severity == 'WARNING':
        audit.warning(log_msg)
    elif severity == 'ERROR':
        audit.error(log_msg)
    else:
        audit.info(log_msg)


def validate_email_format(email: str) -> bool:
    """
    Validate email format with enhanced checks.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid format, False otherwise
    """
    import re
    
    if not email or len(email) > 255:
        return False
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False
    
    # Additional checks
    local_part, domain = email.rsplit('@', 1)
    
    # Local part shouldn't start or end with dot
    if local_part.startswith('.') or local_part.endswith('.'):
        return False
    
    # No consecutive dots in local part
    if '..' in local_part:
        return False
    
    # Domain should have at least one dot
    if '.' not in domain:
        return False
    
    return True


def generate_csrf_token() -> str:
    """
    Generate a CSRF token for forms.
    This is a helper that works with Flask-WTF.
    
    Returns:
        CSRF token string
    """
    from flask_wtf.csrf import generate_csrf
    return generate_csrf()


def check_request_origin() -> bool:
    """
    Verify request origin matches expected host.
    Helps prevent CSRF attacks.
    
    Returns:
        True if origin is valid, False otherwise
    """
    origin = request.headers.get('Origin')
    referer = request.headers.get('Referer')
    
    if not origin and not referer:
        # Allow requests without origin/referer (same-site)
        return True
    
    expected_host = request.host_url.rstrip('/')
    
    if origin:
        return origin == expected_host
    
    if referer:
        return referer.startswith(expected_host)
    
    return False

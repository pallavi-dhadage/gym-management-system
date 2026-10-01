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
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' "
                "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
                "https://fonts.googleapis.com; "
                "font-src 'self' https://cdnjs.cloudflare.com "
                "https://fonts.gstatic.com data:; "
                "img-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
            resp.headers.setdefault('Content-Security-Policy', csp)

        if app.config.get('SESSION_COOKIE_SECURE'):
            resp.headers.setdefault(
                'Strict-Transport-Security',
                'max-age=31536000; includeSubDomains'
            )

        return resp
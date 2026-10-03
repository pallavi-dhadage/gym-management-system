# SetFit Gym — Security Overview

This document lists the security controls implemented in the SetFit Gym Flask application.

## Threat Model

Assets worth protecting:
- User credentials (email + password)
- Membership and payment records (UTR numbers, amounts, statuses)
- Trainer notes (personal training data)
- Admin actions (verification, activation, reminders)

Trust boundaries:
- Public internet → Flask app
- Flask app → SQLite (local)
- Flask app → external CDNs (Bootstrap, Font Awesome, Google Fonts)

## OWASP Top 10 — Coverage

### A01. Broken Access Control
- ✅ All routes use `@login_required` unless public by design (`/`, `/pricing`, `/enquiry`, `/auth/*`).
- ✅ Role-based gate `@role_required('admin')` / `@role_required('trainer','admin')` on admin/trainer areas.
- ✅ Member-scoped queries (`filter_by(member_id=current_user.id)`) prevent IDOR.
- ✅ 404 (not 403) returned for unknown resource IDs, avoiding enumeration.
- ✅ `login_manager.session_protection = 'strong'` invalidates sessions on IP/UA change.

### A02. Cryptographic Failures
- ✅ Passwords hashed with **PBKDF2-SHA256, 600,000 iterations** (Werkzeug default).
- ✅ Session cookie signed with `SECRET_KEY` from env, never committed.
- ✅ `SESSION_COOKIE_HTTPONLY=True`, `SAMESITE=Lax`; `Secure=True` in production.
- ✅ No PII or secrets in logs (audit logger strips sensitive keys).

### A03. Injection
- ✅ All DB access via SQLAlchemy ORM (parameterised).
- ✅ No raw SQL with string interpolation anywhere.
- ✅ Jinja2 auto-escaping on by default; no `|safe` on user content.
- ✅ UTR inputs validated by strict regex `^[A-Za-z0-9\-]+$`.

### A04. Insecure Design
- ✅ Membership activation requires **admin verification** of payment.
- ✅ UTR uniqueness enforced at DB level (unique index) + app check.
- ✅ Plan changes only allowed in `pending` state.
- ✅ Membership amount snapshot at submission, so later plan changes don't affect pending payment.

### A05. Security Misconfiguration
- ✅ `WTF_CSRF_ENABLED=True` globally; every form includes `hidden_tag()`.
- ✅ `DEBUG=False` in production config; `SECRET_KEY` required.
- ✅ Security headers middleware (see `app/utils/security.py`): CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy.
- ✅ `SESSION_COOKIE_SECURE=True` under production.

### A06. Vulnerable & Outdated Components
- ✅ Pinned versions in `requirements.txt`.
- ✅ Minimal dependency surface (Flask, SQLAlchemy, Flask-Login, Flask-WTF, Flask-Limiter, qrcode, Pillow, APScheduler).

### A07. Identification & Authentication Failures
- ✅ Login rate-limited (20/hour/IP), register (10/hour/IP).
- ✅ Identical error message for "unknown email" vs "wrong password" (no enumeration).
- ✅ Inactive accounts blocked at login.
- ✅ Audit log records `LOGIN_SUCCESS`, `LOGIN_FAIL`, `LOGIN_BLOCKED_INACTIVE`, `LOGOUT`.

### A08. Software & Data Integrity Failures
- ✅ No deserialization of untrusted data (no `pickle`, no `eval`).
- ✅ Payment transitions (`submitted → verified|rejected`) are one-way and idempotent.

### A09. Security Logging & Monitoring Failures
- ✅ Dedicated `logs/audit.log` (rotating, 10 MB × 10 backups).
- ✅ Application log `logs/app.log` (10 MB × 5 backups).
- ✅ Error log `logs/error.log` (10 MB × 5 backups).
- ✅ Security events tagged with `SECURITY` prefix: 400/401/403/429.
- ✅ Audit events: `LEAD_*`, `PAYMENT_*`, `MEMBERSHIP_*`, `NOTE_*`, `REMINDER_SENT`, `DAILY_JOB_RUN`, `ADMIN_*`.

### A10. Server-Side Request Forgery (SSRF)
- ✅ App makes no outbound HTTP requests based on user input.
- ✅ UPI QR data is generated locally (no external API calls).

## Additional Controls

- **CSRF**: Flask-WTF on all state-changing forms.
- **Rate limiting**: Flask-Limiter; stricter limits on auth and enquiry routes.
- **Honeypot field** on public enquiry form silently drops bot submissions.
- **Safe redirects**: `is_safe_url()` only allows same-host redirects after login.
- **Audit trail**: admin actions recorded with actor email, IP, timestamp.
- **Scheduler isolation**: APScheduler runs only in the Flask child process; disabled under testing.
- **Secret hygiene**: `.env` excluded via `.gitignore`; production secrets from environment only.
- **Enhanced CSP**: Updated Content Security Policy to allow GSAP animations and Unsplash images while maintaining security.
- **Input validation**: Strict validation on all user inputs including UTR format, email format, and filename sanitization.
- **Password strength**: Enhanced password validation beyond basic requirements, checking for common weak passwords.
- **Request origin verification**: Check origin and referer headers to prevent CSRF attacks.
- **Security logging**: Structured logging of all security events with IP, user agent, and referer information.
- **Error handling**: Enhanced error handlers with detailed security logging and proper JSON/HTML responses.
- **File upload safety**: Filename sanitization to prevent path traversal attacks.
- **Email validation**: Enhanced email format validation with additional checks for malformed addresses.

## Security Enhancements (Module 8)

### Frontend Security
- Animations respect `prefers-reduced-motion` for accessibility
- All external resources loaded from trusted CDNs only
- Background images loaded via HTTPS from Unsplash
- No inline JavaScript except for GSAP initialization
- CSRF tokens included in all forms

### Backend Security
- Enhanced error logging with IP, user agent, and referer tracking
- Password strength validation beyond basic requirements
- UTR format validation with strict regex patterns
- Email format validation with malformed address detection
- Filename sanitization for upload safety
- Request origin verification for CSRF prevention

### Monitoring & Logging
- Security events logged with structured data
- Enhanced audit trail with detailed context
- Separate logging for security vs application events
- Rate limit violations logged with full request context
- Unhandled exceptions logged with IP and request details

## Responsible Disclosure

Report vulnerabilities to: **security@setfitgym.com**

Please include:
- Affected endpoint / version
- Steps to reproduce
- Impact assessment

We aim to acknowledge within 48 hours.
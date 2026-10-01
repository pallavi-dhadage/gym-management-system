# GymMS — Gym Management System

A production-ready Flask application for managing gym memberships, UPI payments, personalized training notes, and automated renewal reminders.

## Features

- **Public landing page** with pricing and free-trial enquiry form
- **Secure auth** — PBKDF2-SHA256 (600k iterations), CSRF, rate limiting, audit logs
- **Role-based access** — `member`, `trainer`, `admin`
- **Membership lifecycle** — `pending → active → expired`
- **UPI payments** with QR code, UTR submission, admin verification
- **Trainer notes** — workout/diet plans visible to each member
- **Automated scheduler** — daily expiry + renewal reminders
- **Admin dashboard** — leads, payments, expiring memberships

## Tech Stack

Flask 3 · SQLAlchemy · Flask-Login · Flask-WTF · Flask-Limiter · APScheduler · Bootstrap 5 · gunicorn

## Local Development

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/gym-management-system.git
cd gym-management-system
```

### 2. Virtual environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment

```bash
cp .env.example .env
```

Generate a secret key and set it in `.env`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Initialize DB + seed plans + create admin

```bash
$env:FLASK_APP = "run.py"      # Windows PowerShell
# export FLASK_APP=run.py      # macOS / Linux

flask seed-plans
flask create-admin
```

### 6. Run

```bash
python run.py
```

Open **http://127.0.0.1:5000**

## CLI Commands

| Command | Purpose |
|---------|---------|
| `flask create-admin` | Create an admin user |
| `flask create-trainer` | Create a trainer user |
| `flask list-users` | List all users |
| `flask seed-plans` | Seed default membership plans (idempotent) |
| `flask run-expiry-check` | Run the daily expiry job once |

## Testing

```bash
python -m pytest tests/ -v
```

Expected: **80 passing tests** across auth, leads, membership, payments, notes, scheduler, and security.

## Project Structure

```
gym-management-system/
├── app/
│   ├── __init__.py           # Application factory
│   ├── cli.py                # Flask CLI commands
│   ├── models/               # SQLAlchemy models
│   ├── routes/               # Blueprints (main, auth, admin, member, trainer)
│   ├── services/             # UPI QR, notifications, scheduler
│   ├── utils/                # Logging, errors, decorators, security
│   ├── templates/            # Jinja2 templates
│   └── static/               # CSS, JS, images
├── instance/                 # SQLite database (gitignored)
├── logs/                     # Rotating logs (gitignored)
├── tests/                    # Pytest suite
├── wsgi.py                   # Production WSGI entrypoint
├── run.py                    # Dev server entrypoint
├── config.py                 # Config classes
└── requirements.txt
```

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for a step-by-step Ubuntu + gunicorn + nginx + systemd guide.

Quick start:

```bash
export FLASK_ENV=production
export SECRET_KEY="<your-64-char-secret>"
export SESSION_COOKIE_SECURE=True

gunicorn -w 1 -b 0.0.0.0:8000 wsgi:app
```

> Use **1 gunicorn worker** with SQLite. Switch to Postgres for >1 worker.

## Security

See [SECURITY.md](SECURITY.md) for the full threat model and OWASP Top 10 coverage.

Key controls:
- CSRF protection on all forms
- CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- Rate limiting on auth and public routes
- Audit log for all sensitive actions
- Safe redirects, no open-redirect vulnerabilities
- No user enumeration in auth

## License

MIT
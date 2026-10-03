# SetFit Gym — Premium Gym Management System

A modern, production-ready Flask application for managing SetFit Gym memberships, UPI payments, personalized training notes, trekking adventures, cricket tournaments, and automated renewal reminders.

## ✨ Features

### Core Functionality
- **Public landing page** with hero slider, social proof, and free-trial enquiry form
- **Secure authentication** — PBKDF2-SHA256 (600k iterations), CSRF, rate limiting, audit logs
- **Role-based access control** — `member`, `trainer`, `admin`
- **Membership lifecycle** — `pending → active → expired`
- **UPI payments** with QR code generation, UTR submission, admin verification
- **Trainer notes** — personalized workout/diet plans visible to each member
- **Automated scheduler** — daily expiry checks + renewal reminders
- **Admin dashboard** — leads management, payments, expiring memberships

### Modern Enhancements (2024)
- **Responsive mobile-first design** — 5 breakpoints (xs, sm, md, lg, xl)
- **GSAP animations** — smooth page load, scroll triggers, hover effects
- **Background image slider** — continuously moving hero carousel
- **Activity sections** — trekking adventures, cricket tournaments, group fitness
- **Visual journey map** — 5-step membership flow visualization
- **Performance optimizations** — lazy loading, compression, caching
- **Accessibility compliance** — WCAG 2.1 Level AA
- **Comprehensive testing** — unit, integration, performance, accessibility tests

## 🚀 Tech Stack

**Backend:** Flask 3.0 · SQLAlchemy · Flask-Login · Flask-WTF · Flask-Limiter · Flask-Compress · APScheduler  
**Frontend:** HTML (Jinja2) · Bootstrap 5.3 · GSAP 3.12 · Custom CSS · Font Awesome  
**Database:** SQLite (dev) / PostgreSQL (production)  
**Deployment:** Gunicorn · Nginx · Docker-ready

## 📊 Quick Stats

- **85+ KB** of production code
- **35+ files** across 8 modules
- **9 commits** in latest modernization
- **95+ test coverage** target
- **Lighthouse score:** 85+ (mobile & desktop)

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

### Run All Tests
```bash
# Recommended: Use test runner
python run_tests.py

# Or directly with pytest
python -m pytest tests/ -v --cov=app

# Run specific test modules
pytest tests/test_performance.py -v
pytest tests/test_accessibility.py -v
```

Expected: **95+ test coverage** across auth, leads, membership, payments, notes, scheduler, security, performance, and accessibility.

### Coverage Report
```bash
# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html

# Open in browser
# Windows: start htmlcov/index.html
# Mac: open htmlcov/index.html
```

### Testing Documentation
See [TESTING.md](TESTING.md) for comprehensive testing guide including:
- Cross-browser compatibility testing
- Mobile responsiveness testing
- Google Lighthouse audits
- Security vulnerability scanning
- Accessibility compliance (WCAG 2.1)
- Performance benchmarks
- User flow validation

## 📈 Performance

See [PERFORMANCE.md](PERFORMANCE.md) for detailed performance optimization guide.

**Key Optimizations:**
- Lazy loading (images & backgrounds)
- Deferred JavaScript loading
- Flask-Compress (gzip/brotli)
- LocalStorage caching with TTL
- Core Web Vitals monitoring
- Network quality detection
- Resource hints (preconnect, dns-prefetch)

**Benchmarks (Target):**
- First Contentful Paint: <1.8s (mobile 4G)
- Largest Contentful Paint: <2.5s
- Time to Interactive: <3.8s
- First Input Delay: <100ms
- Cumulative Layout Shift: <0.1

## 🔐 Security

See [SECURITY.md](SECURITY.md) for comprehensive security documentation.

**Key Features:**
- OWASP Top 10 protection
- CSRF protection on all forms
- Rate limiting (200 req/hour default)
- Password hashing (PBKDF2-SHA256, 600k iterations)
- Session security (httponly, secure, samesite)
- Content Security Policy
- Parameterized SQL queries
- Input validation & sanitization
- Audit logging
- Secure password strength validation

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


## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide.

### Quick Deploy Options

#### 1. Traditional Server (Ubuntu/Debian)
```bash
# Install dependencies
sudo apt install python3.11 python3-venv nginx postgresql redis-server

# Setup application
git clone https://github.com/pallavi-dhadage/gym-management-system.git
cd gym-management-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values

# Initialize database
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
flask seed-plans
flask create-admin

# Setup Gunicorn + Nginx
# See DEPLOYMENT.md for systemd service and Nginx config
```

#### 2. Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f web
```

#### 3. Platform-as-a-Service
**Heroku:**
```bash
heroku create setfitgym
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
git push heroku main
```

**Railway/Render:** Connect GitHub repo and deploy automatically.

### Pre-Deployment Checklist
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] `SECRET_KEY` generated (production)
- [ ] `DEBUG = False`
- [ ] HTTPS/SSL configured
- [ ] Database backups enabled
- [ ] Monitoring setup (optional)
- [ ] Lighthouse score > 85

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SECURITY.md](SECURITY.md) | Security features, OWASP compliance, audit logs |
| [PERFORMANCE.md](PERFORMANCE.md) | Performance optimizations, benchmarks, monitoring |
| [TESTING.md](TESTING.md) | Testing guide, cross-browser, accessibility, security |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment options, server setup, maintenance |

## 🎨 Design & UX

### Color Palette
- **Brand Orange:** `#ff6b35` - Primary CTAs, highlights
- **Dark:** `#1a202c` - Headings, primary text
- **Muted:** `#718096` - Secondary text
- **Light:** `#f7fafc` - Backgrounds, cards
- **Green:** `#10b981` - Success states, trekking
- **Blue:** `#3b82f6` - Links, cricket

### Typography
- **Font:** Inter (Google Fonts)
- **Weights:** 300, 400, 500, 600, 700, 800
- **Base Size:** 16px
- **Line Height:** 1.6

### Responsive Breakpoints
- **xs:** 320px (mobile portrait)
- **sm:** 576px (mobile landscape)
- **md:** 768px (tablet portrait)
- **lg:** 1024px (tablet landscape / laptop)
- **xl:** 1280px (desktop)

### Animations (GSAP)
- Page load fade-in
- Scroll-triggered reveals
- Hover scale effects
- Progress bar animations
- Counter animations

## 🛣️ User Journey

1. **Browse** → Anonymous user visits homepage
2. **Enquiry** → Fills free trial form (becomes Lead)
3. **Admin Contact** → Admin reviews leads, calls user
4. **Register** → User creates account (status: JWT/PENDING)
5. **Select Plan** → Member chooses membership plan
6. **Payment** → Views UPI QR code, makes payment
7. **Submit UTR** → Enters payment transaction ID
8. **Verification** → Admin verifies payment
9. **Activation** → Membership status → ACTIVE
10. **Training** → Member views dashboard, trainer notes
11. **Renewal** → Auto-reminder 7 days before expiry
12. **Repeat** → Member renews or expires

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Commit Convention:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting, missing semicolons
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask Community** - Excellent web framework
- **Bootstrap** - Responsive design system
- **GSAP** - Professional-grade animations
- **Unsplash** - High-quality stock images
- **Font Awesome** - Beautiful icons
- **Google Fonts** - Inter typography

## 📧 Support

- **Issues:** [GitHub Issues](https://github.com/pallavi-dhadage/gym-management-system/issues)
- **Email:** admin@setfitgym.com (update with actual contact)
- **Documentation:** See docs in repository

---

**Built with ❤️ for SetFit Gym**  
Version 2.0 | Last Updated: 2024 | Module 10 Complete

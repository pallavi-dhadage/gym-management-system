# Deployment Guide - SetFit Gym Management System

## Pre-Deployment Checklist

### ✅ Code Quality
- [ ] All tests passing (`python run_tests.py`)
- [ ] Code reviewed and approved
- [ ] No console errors or warnings
- [ ] Documentation up to date
- [ ] CHANGELOG updated with new features

### ✅ Security
- [ ] All secrets in environment variables (not in code)
- [ ] `SECRET_KEY` generated and secure
- [ ] `DEBUG = False` in production
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] HTTPS/SSL certificate configured
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Content Security Policy active
- [ ] No exposed admin credentials
- [ ] Database credentials secured

### ✅ Database
- [ ] Database backups configured
- [ ] Migrations tested
- [ ] Database indexes optimized
- [ ] Foreign key constraints verified
- [ ] Connection pooling configured

### ✅ Performance
- [ ] Lighthouse score > 85 (mobile & desktop)
- [ ] Core Web Vitals meet targets
- [ ] Static files compressed
- [ ] Image optimization complete
- [ ] CDN configured (optional)
- [ ] Caching headers set correctly

### ✅ Monitoring
- [ ] Error logging configured (Sentry/CloudWatch)
- [ ] Application monitoring (New Relic/Datadog)
- [ ] Server monitoring (CPU, memory, disk)
- [ ] Uptime monitoring (UptimeRobot/Pingdom)
- [ ] Alert notifications configured

---

## Environment Setup

### Required Environment Variables

```bash
# .env file for production

# Application
FLASK_ENV=production
SECRET_KEY=<generate-with-secrets.token_hex-32>

# Database
DATABASE_URL=postgresql://user:password@host:5432/gym_db
# Or SQLite: sqlite:///absolute/path/to/gym.db

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=3600

# Rate Limiting
RATELIMIT_STORAGE_URI=redis://localhost:6379/0
RATELIMIT_DEFAULT=200 per hour
RATELIMIT_ENABLED=True

# UPI Payment
UPI_ID=your-gym@upi
UPI_PAYEE_NAME=SetFit Gym

# Email (if SMTP configured)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=app-specific-password
ADMIN_EMAIL=admin@setfitgym.com

# Scheduler
SCHEDULER_ENABLED=True
SCHEDULER_HOUR=2
MEMBERSHIP_REMINDER_DAYS=7

# Logging
LOG_LEVEL=WARNING
LOG_DIR=/var/log/setfit-gym
```

### Generate SECRET_KEY

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Deployment Options

### Option 1: Traditional Server (Ubuntu/Debian)

#### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install PostgreSQL (recommended) or use SQLite
sudo apt install postgresql postgresql-contrib -y

# Install Nginx
sudo apt install nginx -y

# Install Redis (for rate limiting)
sudo apt install redis-server -y
```

#### 2. Setup Application

```bash
# Create app user
sudo useradd -m -s /bin/bash setfitgym

# Switch to app user
sudo su - setfitgym

# Clone repository
git clone https://github.com/pallavi-dhadage/gym-management-system.git
cd gym-management-system

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create production .env file
cp .env.example .env
nano .env  # Edit with production values
```

#### 3. Setup Database

**PostgreSQL:**
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE gym_db;
CREATE USER gym_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE gym_db TO gym_user;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://gym_user:secure_password@localhost:5432/gym_db
```

**SQLite (simpler for small deployments):**
```bash
# Already works out of the box
# Just ensure proper permissions
mkdir -p instance
chmod 750 instance
```

#### 4. Initialize Database

```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Create admin user
python cli.py seed-admin
```

#### 5. Setup Gunicorn Service

```bash
# Exit app user
exit

# Create systemd service
sudo nano /etc/systemd/system/setfitgym.service
```

```ini
[Unit]
Description=SetFit Gym Management System
After=network.target

[Service]
User=setfitgym
Group=setfitgym
WorkingDirectory=/home/setfitgym/gym-management-system
Environment="PATH=/home/setfitgym/gym-management-system/venv/bin"
ExecStart=/home/setfitgym/gym-management-system/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/home/setfitgym/gym-management-system/setfitgym.sock \
    --access-logfile /var/log/setfit-gym/access.log \
    --error-logfile /var/log/setfit-gym/error.log \
    --log-level warning \
    "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/setfit-gym
sudo chown setfitgym:setfitgym /var/log/setfit-gym

# Enable and start service
sudo systemctl enable setfitgym
sudo systemctl start setfitgym
sudo systemctl status setfitgym
```

#### 6. Setup Nginx

```bash
sudo nano /etc/nginx/sites-available/setfitgym
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL certificates (use certbot for Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static {
        alias /home/setfitgym/gym-management-system/app/static;
        expires 12h;
        add_header Cache-Control "public, immutable";
    }

    # Application
    location / {
        proxy_pass http://unix:/home/setfitgym/gym-management-system/setfitgym.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Increase max upload size (for images)
    client_max_body_size 10M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/setfitgym /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 7. Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
sudo certbot renew --dry-run  # Test renewal
```

---

### Option 2: Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://gym_user:password@db:5432/gym_db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./instance:/app/instance
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    restart: always

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=gym_db
      - POSTGRES_USER=gym_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
```

```bash
# Deploy with Docker Compose
docker-compose up -d
docker-compose logs -f web
```

---

### Option 3: Platform-as-a-Service (PaaS)

#### Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn app:create_app()" > Procfile

# Deploy
heroku login
heroku create setfitgym
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
git push heroku main
heroku run python cli.py seed-admin
heroku open
```

#### Railway/Render

1. Connect GitHub repository
2. Set environment variables in dashboard
3. Deploy automatically on push
4. Add PostgreSQL and Redis add-ons

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Check service status
sudo systemctl status setfitgym

# Check logs
sudo tail -f /var/log/setfit-gym/error.log
sudo journalctl -u setfitgym -f

# Test endpoints
curl https://your-domain.com
curl https://your-domain.com/auth/login
```

### 2. Create Admin User

```bash
# If not done during deployment
cd /home/setfitgym/gym-management-system
source venv/bin/activate
python cli.py seed-admin
```

### 3. Setup Backups

**Database Backups:**
```bash
# Create backup script
sudo nano /usr/local/bin/backup-setfitgym.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/setfitgym"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump -U gym_user gym_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# SQLite backup (if using SQLite)
# cp /home/setfitgym/gym-management-system/instance/gym.db $BACKUP_DIR/gym_$DATE.db

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x /usr/local/bin/backup-setfitgym.sh

# Schedule with cron
sudo crontab -e
# Add: 0 3 * * * /usr/local/bin/backup-setfitgym.sh
```

### 4. Monitoring Setup

**Uptime Monitoring:**
- [UptimeRobot](https://uptimerobot.com/) - Free
- [Pingdom](https://www.pingdom.com/)

**Error Tracking:**
```python
# Install Sentry
pip install sentry-sdk[flask]

# Add to app/__init__.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,
    environment=os.environ.get('FLASK_ENV', 'production')
)
```

### 5. Performance Monitoring

```bash
# Monitor server resources
htop  # CPU, memory
df -h  # Disk space
iostat  # I/O stats

# Monitor application
# Check Gunicorn worker status
ps aux | grep gunicorn

# Monitor database connections
# PostgreSQL:
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

---

## Maintenance

### Update Application

```bash
# Backup first!
/usr/local/bin/backup-setfitgym.sh

# Pull updates
sudo su - setfitgym
cd gym-management-system
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Run migrations (if any)
# Apply database changes

# Restart service
exit
sudo systemctl restart setfitgym
sudo systemctl status setfitgym
```

### View Logs

```bash
# Application logs
sudo tail -f /var/log/setfit-gym/error.log
sudo tail -f /var/log/setfit-gym/access.log

# System logs
sudo journalctl -u setfitgym -n 100 --no-pager

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Database Maintenance

```bash
# PostgreSQL vacuum and analyze
sudo -u postgres psql gym_db -c "VACUUM ANALYZE;"

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('gym_db'));"

# SQLite optimize
sqlite3 instance/gym.db "VACUUM;"
```

---

## Rollback Procedure

If something goes wrong:

```bash
# Stop service
sudo systemctl stop setfitgym

# Restore from backup
cd /home/setfitgym/gym-management-system
git checkout <previous-commit-hash>

# Restore database
# PostgreSQL:
gunzip < /var/backups/setfitgym/db_YYYYMMDD_HHMMSS.sql.gz | psql -U gym_user gym_db

# SQLite:
# cp /var/backups/setfitgym/gym_YYYYMMDD_HHMMSS.db instance/gym.db

# Restart service
sudo systemctl start setfitgym
```

---

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (Nginx/HAProxy)
- Multiple Gunicorn instances
- Shared database (PostgreSQL)
- Shared session store (Redis)
- CDN for static assets

### Vertical Scaling
- Increase Gunicorn workers (2-4 per CPU core)
- Increase database resources
- Optimize queries with indexes

### Caching
- Redis for session storage
- CDN for static assets (CloudFlare/AWS CloudFront)
- Database query caching

---

## Troubleshooting

### Common Issues

**1. 502 Bad Gateway**
```bash
# Check Gunicorn is running
sudo systemctl status setfitgym
# Check socket file exists
ls -la /home/setfitgym/gym-management-system/setfitgym.sock
# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

**2. Database Connection Errors**
```bash
# Check database is running
sudo systemctl status postgresql
# Test connection
psql -U gym_user -d gym_db -h localhost
# Check DATABASE_URL in .env
```

**3. High CPU Usage**
```bash
# Check worker count
ps aux | grep gunicorn | wc -l
# Reduce workers if too many
# Check for slow queries
# Enable query logging in PostgreSQL
```

**4. Disk Space Full**
```bash
# Check disk usage
df -h
# Clean old logs
sudo find /var/log -name "*.log" -mtime +30 -delete
# Clean old backups
find /var/backups/setfitgym -mtime +30 -delete
```

---

## Support

- **Documentation:** See README.md, TESTING.md, PERFORMANCE.md
- **Issues:** GitHub Issues
- **Email:** admin@setfitgym.com (update with actual contact)

---

**Last Updated:** Module 10 - Testing & Validation  
**Maintained By:** SetFit Gym Development Team

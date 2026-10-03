# Testing & Validation Guide

## Overview
Comprehensive testing and validation procedures for SetFit Gym management system covering functionality, security, performance, accessibility, and cross-browser compatibility.

## Testing Checklist

### ✅ Module 10 Testing Scope
- [ ] Cross-browser compatibility testing
- [ ] Mobile device responsiveness
- [ ] Google Lighthouse audit
- [ ] Security vulnerability scan
- [ ] Accessibility compliance (WCAG 2.1)
- [ ] Performance benchmarks
- [ ] User flow validation
- [ ] API endpoint testing
- [ ] Database integrity checks
- [ ] Error handling verification

---

## 1. Cross-Browser Testing

### Desktop Browsers

#### Chrome (Latest)
**Test Areas:**
- [ ] Hero slider animation
- [ ] GSAP scroll triggers
- [ ] Form submissions with CSRF
- [ ] Dashboard progress bars
- [ ] Payment flow with QR code
- [ ] Journey map visualization

**Commands:**
```bash
# Open in Chrome
start chrome http://localhost:5000
```

#### Firefox (Latest)
**Test Areas:**
- [ ] CSS Grid/Flexbox layouts
- [ ] Font rendering (Inter font)
- [ ] Background image lazy loading
- [ ] LocalStorage caching
- [ ] WebP fallback handling

**Commands:**
```bash
# Open in Firefox
start firefox http://localhost:5000
```

#### Edge (Latest)
**Test Areas:**
- [ ] Bootstrap components
- [ ] Responsive breakpoints
- [ ] Form validation
- [ ] Session management

**Commands:**
```bash
# Open in Edge
start msedge http://localhost:5000
```

#### Safari (Mac/iOS)
**Test Areas:**
- [ ] webkit-specific CSS properties
- [ ] Touch gestures
- [ ] Date/time inputs
- [ ] Intersection Observer API

### Mobile Browsers

#### Chrome Mobile (Android)
**Test Areas:**
- [ ] Mobile navigation menu
- [ ] Touch targets (44px minimum)
- [ ] Viewport scaling
- [ ] Form inputs on mobile keyboard
- [ ] Payment QR code scanning

#### Safari Mobile (iOS)
**Test Areas:**
- [ ] iOS-specific styling
- [ ] Safe area insets
- [ ] -webkit-appearance
- [ ] Touch gestures

### Browser Compatibility Matrix

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Hero Slider | ✅ | ✅ | ✅ | ✅ |
| GSAP Animations | ✅ | ✅ | ✅ | ✅ |
| Lazy Loading | ✅ | ✅ | ✅ 15.4+ | ✅ |
| Flexbox/Grid | ✅ | ✅ | ✅ | ✅ |
| LocalStorage | ✅ | ✅ | ✅ | ✅ |
| WebP Images | ✅ | ✅ 65+ | ✅ 14+ | ✅ 18+ |

---

## 2. Responsive Design Testing

### Breakpoints to Test

#### Mobile (320px - 767px)
```css
/* xs: 320px, sm: 576px */
```
**Test On:**
- iPhone SE (375x667)
- iPhone 12 Pro (390x844)
- Samsung Galaxy S21 (360x800)
- Pixel 5 (393x851)

**Verify:**
- [ ] Single column layout
- [ ] Mobile navigation hamburger
- [ ] Touch-friendly buttons (min 44x44px)
- [ ] Hero text readable
- [ ] Forms stack vertically
- [ ] Testimonial cards readable

#### Tablet (768px - 1023px)
```css
/* md: 768px */
```
**Test On:**
- iPad (768x1024)
- iPad Air (820x1180)
- Surface Pro (912x1368)

**Verify:**
- [ ] 2-column layout where appropriate
- [ ] Readable font sizes
- [ ] Proper spacing
- [ ] Dashboard grid adapts

#### Desktop (1024px+)
```css
/* lg: 1024px, xl: 1280px */
```
**Test On:**
- 1366x768 (common laptop)
- 1920x1080 (Full HD)
- 2560x1440 (2K)

**Verify:**
- [ ] Multi-column layouts
- [ ] Full-width hero
- [ ] Desktop navigation
- [ ] Optimal line lengths (60-80 chars)

### Chrome DevTools Testing
```javascript
// Open DevTools > Toggle Device Toolbar (Ctrl+Shift+M)
// Test each preset device
// Check Elements > Styles for active media queries
```

### Responsive Test Checklist
- [ ] No horizontal scrolling on any device
- [ ] All text readable without zooming
- [ ] Images scale proportionally
- [ ] Navigation accessible on all sizes
- [ ] Forms usable on mobile
- [ ] CTAs visible above the fold
- [ ] Footer content accessible

---

## 3. Google Lighthouse Audit

### Running Lighthouse

#### Chrome DevTools Method
```bash
1. Open Chrome DevTools (F12)
2. Go to "Lighthouse" tab
3. Select categories:
   ✅ Performance
   ✅ Accessibility
   ✅ Best Practices
   ✅ SEO
   ✅ Progressive Web App (optional)
4. Choose device: Mobile & Desktop (run both)
5. Click "Analyze page load"
```

#### CLI Method
```bash
npm install -g lighthouse

# Mobile audit
lighthouse http://localhost:5000 --output html --output-path ./lighthouse-mobile.html --preset=mobile

# Desktop audit
lighthouse http://localhost:5000 --output html --output-path ./lighthouse-desktop.html --preset=desktop
```

### Target Scores

#### Mobile
| Category | Target | Description |
|----------|--------|-------------|
| Performance | 85+ | Load speed, FCP, LCP |
| Accessibility | 95+ | ARIA, contrast, labels |
| Best Practices | 95+ | HTTPS, console errors |
| SEO | 90+ | Meta tags, structure |

#### Desktop
| Category | Target | Description |
|----------|--------|-------------|
| Performance | 90+ | Faster on desktop |
| Accessibility | 95+ | Same as mobile |
| Best Practices | 95+ | Same as mobile |
| SEO | 90+ | Same as mobile |

### Common Issues & Fixes

#### Performance Issues
```
❌ Largest Contentful Paint > 2.5s
Fix: Preload hero image, optimize image size

❌ Total Blocking Time > 300ms
Fix: Defer non-critical JS, code splitting

❌ Cumulative Layout Shift > 0.1
Fix: Define image dimensions, reserve space for dynamic content
```

#### Accessibility Issues
```
❌ Missing alt text on images
Fix: Add descriptive alt attributes

❌ Insufficient color contrast
Fix: Ensure 4.5:1 ratio for text

❌ Missing form labels
Fix: Associate labels with inputs
```

#### SEO Issues
```
❌ Missing meta description
Fix: Add unique meta descriptions per page

❌ Non-crawlable links
Fix: Use <a> tags, not onclick handlers
```

---

## 4. Security Testing

### Automated Security Scan

#### OWASP ZAP (Zed Attack Proxy)
```bash
# Download from https://www.zaproxy.org/download/

# Quick scan
zap-cli quick-scan http://localhost:5000

# Full scan
zap-cli active-scan http://localhost:5000
```

#### Safety (Python Dependencies)
```bash
pip install safety
safety check -r requirements.txt
```

### Manual Security Tests

#### 1. CSRF Protection
```bash
# Test: Submit form without CSRF token
curl -X POST http://localhost:5000/auth/login \
  -d "username=test&password=test"
# Expected: 400 Bad Request (CSRF token missing)
```

#### 2. SQL Injection
```python
# Test inputs:
username = "admin' OR '1'='1"
email = "test@test.com'; DROP TABLE users;--"
# Expected: Parameterized queries prevent injection
```

#### 3. XSS (Cross-Site Scripting)
```html
<!-- Test inputs: -->
<script>alert('XSS')</script>
<img src=x onerror="alert('XSS')">
<!-- Expected: Jinja2 auto-escaping prevents XSS -->
```

#### 4. Authentication Bypass
```bash
# Test: Access protected pages without login
curl http://localhost:5000/admin/dashboard
# Expected: 401 Unauthorized or redirect to login
```

#### 5. Rate Limiting
```bash
# Test: Rapid requests
for i in {1..300}; do
  curl http://localhost:5000/auth/login \
    -d "username=test&password=wrong" &
done
# Expected: 429 Too Many Requests after limit
```

#### 6. Password Strength
```python
# Test passwords:
weak = ["password", "12345678", "qwerty"]
# Expected: Rejected with strength requirements
```

#### 7. Session Security
```python
# Check cookies in DevTools:
# - HttpOnly: True
# - Secure: True (in production)
# - SameSite: Lax
```

### Security Checklist
- [ ] CSRF tokens on all forms
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (auto-escaping)
- [ ] Authentication required for protected routes
- [ ] Rate limiting functional
- [ ] Password hashing (bcrypt/werkzeug)
- [ ] Secure session cookies
- [ ] No sensitive data in URLs
- [ ] HTTPS enforced in production
- [ ] Content Security Policy active
- [ ] No exposed secrets in code
- [ ] Input validation on all forms

---

## 5. Accessibility Testing

### Automated Testing

#### axe DevTools (Browser Extension)
```bash
# Install: https://www.deque.com/axe/devtools/
# Chrome/Firefox/Edge extension

1. Open page
2. Open DevTools
3. Click "axe DevTools" tab
4. Click "Scan ALL of my page"
5. Review issues by severity
```

#### WAVE (Web Accessibility Evaluation Tool)
```bash
# Visit: https://wave.webaim.org/
# Enter URL and run evaluation
# Or install browser extension
```

### Manual Accessibility Tests

#### 1. Keyboard Navigation
```bash
Test: Navigate entire site using only keyboard
- Tab: Move forward
- Shift+Tab: Move backward
- Enter: Activate links/buttons
- Space: Toggle checkboxes
- Esc: Close modals

Verify:
- [ ] All interactive elements reachable
- [ ] Visible focus indicators
- [ ] Logical tab order
- [ ] No keyboard traps
- [ ] Skip links functional
```

#### 2. Screen Reader Testing

**NVDA (Windows - Free)**
```bash
# Download: https://www.nvaccess.org/download/

Test:
- [ ] Page structure announced
- [ ] Form labels read correctly
- [ ] Button purposes clear
- [ ] Image alt text descriptive
- [ ] Link text meaningful
```

**JAWS (Windows - Commercial)**
```bash
# Trial: https://www.freedomscientific.com/downloads/

Test same as NVDA
```

**VoiceOver (Mac/iOS - Built-in)**
```bash
# Enable: System Preferences > Accessibility > VoiceOver

Mac: Cmd+F5 to toggle
iOS: Settings > Accessibility > VoiceOver

Test same elements
```

#### 3. Color Contrast
```bash
# Tool: https://webaim.org/resources/contrastchecker/

Test combinations:
- [ ] Body text on background: 4.5:1 minimum
- [ ] Headings: 4.5:1 minimum
- [ ] Buttons: 4.5:1 minimum
- [ ] Form inputs: 3:1 minimum
- [ ] Focus indicators: 3:1 minimum

SetFit Gym colors:
- Brand orange: #ff6b35 on white
- Dark text: #1a202c on white
- Muted text: #718096 on white (check this)
```

#### 4. Zoom & Text Resize
```bash
Test: Zoom to 200% (Ctrl/Cmd + +)
- [ ] No content cutoff
- [ ] No horizontal scrolling
- [ ] All text readable
- [ ] Buttons usable
- [ ] Layout remains functional

Test: Browser text size increase (Settings > Appearance > Font size)
- [ ] Text scales properly
- [ ] No overlap
```

### WCAG 2.1 Level AA Checklist

#### Perceivable
- [ ] Text alternatives for images
- [ ] Captions for video/audio (if applicable)
- [ ] Proper heading hierarchy (h1 → h2 → h3)
- [ ] Color not sole method of conveying info
- [ ] Minimum 4.5:1 contrast ratio

#### Operable
- [ ] All functionality keyboard accessible
- [ ] No keyboard traps
- [ ] Sufficient time for tasks
- [ ] Seizure prevention (no flashing content >3/sec)
- [ ] Descriptive page titles
- [ ] Focus order logical
- [ ] Link purpose clear from text

#### Understandable
- [ ] Language of page identified (lang="en")
- [ ] Consistent navigation
- [ ] Consistent identification
- [ ] Input labels/instructions provided
- [ ] Error identification and suggestions
- [ ] Error prevention (confirmations)

#### Robust
- [ ] Valid HTML (no parsing errors)
- [ ] Name, role, value for custom components
- [ ] Status messages accessible
- [ ] No console errors

---

## 6. Performance Testing

### Core Web Vitals Testing

#### WebPageTest.org
```bash
URL: https://www.webpagetest.org/
Settings:
- Test Location: Mumbai, India (or closest to users)
- Browser: Chrome on Mobile 4G
- Connection: 4G
- Number of Tests: 3 (median result)

Check:
- [ ] First Contentful Paint < 1.8s
- [ ] Largest Contentful Paint < 2.5s
- [ ] Total Blocking Time < 300ms
- [ ] Cumulative Layout Shift < 0.1
- [ ] Speed Index < 3.4s
```

#### Chrome User Experience Report (CrUX)
```bash
# Once deployed to production:
Visit: https://developers.google.com/speed/pagespeed/insights/
Enter production URL
View field data (real user metrics)
```

### Load Testing

#### Apache Bench (ab)
```bash
# Install: sudo apt-get install apache2-utils (Linux)
#          brew install ab (Mac)

# Test homepage
ab -n 1000 -c 10 http://localhost:5000/
# -n 1000: Total requests
# -c 10: Concurrent requests

Check:
- Requests per second > 50
- Time per request < 200ms
- Failed requests = 0
```

#### Locust (Python Load Testing)
```bash
pip install locust

# Create locustfile.py:
from locust import HttpUser, task, between

class GymUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def homepage(self):
        self.client.get("/")
    
    @task
    def login_page(self):
        self.client.get("/auth/login")

# Run:
locust -f locustfile.py --host=http://localhost:5000

# Open http://localhost:8089 and start test
# Try: 100 users, 10 users/sec spawn rate
```

### Performance Benchmarks

#### Target Metrics
| Metric | Mobile 4G | Desktop |
|--------|-----------|---------|
| First Paint | <1.8s | <0.8s |
| FCP | <2.0s | <1.0s |
| LCP | <2.5s | <1.5s |
| TTI | <3.8s | <2.0s |
| FID | <100ms | <50ms |
| CLS | <0.1 | <0.1 |
| Page Size | <2MB | <2MB |
| Requests | <50 | <50 |

---

## 7. User Flow Validation

### Critical User Journeys

#### Journey 1: Browse → Enquiry
```bash
1. Visit homepage
2. View plans
3. Scroll to enquiry form
4. Fill form (valid data)
5. Submit
6. Verify success message
7. Check database for lead entry

Expected: Lead created with status=NEW
```

#### Journey 2: Register → Login
```bash
1. Click "Register"
2. Select a plan
3. Fill registration form
4. Submit
5. Verify success message
6. Login with credentials
7. Check dashboard loads

Expected: User created with role=member, status=JWT
```

#### Journey 3: Payment Flow
```bash
1. Login as member
2. Go to membership page
3. Select plan
4. View QR code
5. Simulate payment (record UTR)
6. Submit UTR
7. Verify pending status

Expected: Payment record created, membership=PENDING
```

#### Journey 4: Admin Verification
```bash
1. Login as admin
2. View payments dashboard
3. Verify pending payment
4. Activate membership
5. Check member dashboard updates

Expected: Membership status=ACTIVE, end_date calculated
```

#### Journey 5: Renewal Reminder
```bash
1. Admin dashboard
2. View expiring memberships
3. Check members expiring in 7 days
4. Verify reminder logic

Expected: Members within MEMBERSHIP_REMINDER_DAYS shown
```

### Flow Testing Checklist
- [ ] Anonymous user can browse
- [ ] Enquiry form creates lead
- [ ] Registration creates user (JWT status)
- [ ] Login works with correct credentials
- [ ] Login fails with wrong credentials
- [ ] Member can view dashboard
- [ ] Member can select plan
- [ ] QR code generates correctly
- [ ] Payment submission stores UTR
- [ ] Admin can verify payments
- [ ] Admin can manage users
- [ ] Trainer can view assigned members
- [ ] Renewal reminders show correctly
- [ ] Session timeout works
- [ ] Logout clears session

---

## 8. Database Testing

### Integrity Tests

#### 1. Referential Integrity
```sql
-- Check orphaned records
SELECT * FROM memberships WHERE user_id NOT IN (SELECT id FROM users);
SELECT * FROM payments WHERE membership_id NOT IN (SELECT id FROM memberships);
SELECT * FROM notes WHERE user_id NOT IN (SELECT id FROM users);

-- Expected: No results (all foreign keys valid)
```

#### 2. Constraint Validation
```python
# Test unique constraints
# Try: Create user with duplicate email
# Expected: IntegrityError

# Test not-null constraints
# Try: Create user without required fields
# Expected: IntegrityError

# Test check constraints
# Try: Create membership with end_date < start_date
# Expected: ValidationError or rejected
```

#### 3. Data Validation
```python
# Test email format
invalid_emails = ["test", "@test.com", "test@", "test@.com"]
# Expected: All rejected

# Test phone format
invalid_phones = ["123", "abcdefghij", "12345"]
# Expected: All rejected

# Test enum values
invalid_status = ["INVALID", "xyz", ""]
# Expected: All rejected
```

### Database Checklist
- [ ] All foreign keys have indexes
- [ ] No orphaned records
- [ ] Unique constraints enforced
- [ ] Not-null constraints enforced
- [ ] Enum values validated
- [ ] Dates logical (end > start)
- [ ] Cascade deletes work correctly
- [ ] Transactions rollback on error

---

## 9. Error Handling Testing

### HTTP Error Pages

#### Test Each Error Page
```bash
# 400 Bad Request
curl -X POST http://localhost:5000/auth/login
# Missing CSRF token

# 401 Unauthorized
curl http://localhost:5000/member/dashboard
# Not logged in

# 403 Forbidden
# Login as member, try to access /admin/dashboard
# Different role

# 404 Not Found
curl http://localhost:5000/nonexistent

# 500 Internal Server Error
# Temporarily break database connection
# Expected: Custom error page, not Flask default
```

#### Error Page Checklist
- [ ] Custom error pages for 400, 401, 403, 404, 500
- [ ] Error pages match site design
- [ ] Links back to homepage
- [ ] No sensitive information exposed
- [ ] Errors logged server-side
- [ ] User-friendly messages

### Form Validation Errors
```bash
Test each form with:
- [ ] Empty required fields
- [ ] Invalid email format
- [ ] Short passwords
- [ ] Mismatched password confirmation
- [ ] Invalid phone numbers
- [ ] SQL injection attempts
- [ ] XSS attempts

Expected: Clear error messages below each field
```

---

## 10. API Endpoint Testing

### Using pytest

```bash
cd gym-management-system
pytest tests/ -v --cov=app
```

### Manual API Testing (curl)

#### Health Check
```bash
curl http://localhost:5000/
# Expected: 200, homepage HTML
```

#### Authentication
```bash
# Register
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&email=test@example.com&password=Test@123&confirm_password=Test@123&csrf_token=TOKEN"

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=Test@123&csrf_token=TOKEN" \
  -c cookies.txt

# Access protected route
curl -b cookies.txt http://localhost:5000/member/dashboard
```

#### Admin Operations
```bash
# View leads (as admin)
curl -b admin_cookies.txt http://localhost:5000/admin/leads

# Verify payment
curl -X POST http://localhost:5000/admin/payments/1/verify \
  -b admin_cookies.txt \
  -d "csrf_token=TOKEN"
```

### API Testing Checklist
- [ ] All endpoints return correct status codes
- [ ] Protected endpoints require authentication
- [ ] Role-based access control works
- [ ] CSRF protection on state-changing operations
- [ ] Rate limiting triggers after threshold
- [ ] JSON responses properly formatted
- [ ] Error responses include helpful messages

---

## Testing Automation

### GitHub Actions CI/CD (Optional)

Create `.github/workflows/test.yml`:
```yaml
name: SetFit Gym Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app
    
    - name: Check security
      run: |
        pip install safety
        safety check -r requirements.txt
    
    - name: Lighthouse CI
      uses: treosh/lighthouse-ci-action@v9
      with:
        urls: |
          http://localhost:5000
        runs: 3
```

---

## Pre-Production Checklist

### Before Deployment
- [ ] All tests passing
- [ ] Lighthouse scores meet targets
- [ ] Security scan shows no critical issues
- [ ] Cross-browser testing complete
- [ ] Mobile testing complete
- [ ] Accessibility audit passed
- [ ] Performance benchmarks met
- [ ] Database migrations ready
- [ ] Environment variables documented
- [ ] Secrets not in code
- [ ] Error logging configured
- [ ] Backup strategy defined
- [ ] SSL certificate ready
- [ ] Domain configured
- [ ] Production config reviewed

### Post-Deployment
- [ ] Smoke tests on production
- [ ] Monitor error rates
- [ ] Check Core Web Vitals
- [ ] Verify SSL/HTTPS
- [ ] Test from multiple locations
- [ ] Monitor server resources
- [ ] Set up alerts
- [ ] Document known issues

---

## Bug Reporting Template

When you find a bug, report it with this structure:

```markdown
### Bug Title
Brief description of the issue

**Environment:**
- Browser: Chrome 120
- OS: Windows 11
- Device: Desktop
- URL: /admin/payments

**Steps to Reproduce:**
1. Login as admin
2. Navigate to payments
3. Click verify on payment #5
4. Observe error

**Expected Behavior:**
Payment should be verified and status changed to ACTIVE

**Actual Behavior:**
500 Internal Server Error shown

**Screenshots:**
[Attach screenshots]

**Console Errors:**
```
TypeError: Cannot read property 'status' of undefined
```

**Severity:** High / Medium / Low
**Priority:** P0 (Critical) / P1 (High) / P2 (Medium) / P3 (Low)
```

---

## Resources

- [Google Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [WebPageTest](https://www.webpagetest.org/)
- [WAVE Accessibility Tool](https://wave.webaim.org/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Can I Use](https://caniuse.com/) - Browser support tables

---

**Last Updated:** Module 10 - Testing & Validation  
**Maintained By:** SetFit Gym Development Team

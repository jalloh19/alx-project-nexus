# 🚀 Production Deployment Checklist

**Project**: ALX Movie Recommendation API
**Date**: February 11, 2026
**Status**: Ready for Deployment

---

## ✅ Pre-Deployment Checklist

### Documentation ✅
- [x] README.md updated with production information
- [x] GETTING_STARTED.md - detailed setup guide
- [x] API_REFERENCE.md - complete endpoint documentation
- [x] PROJECT_STATUS.md - full project metrics
- [x] .env.example updated with all variables
- [x] Swagger UI documentation at /api/docs/
- [x] OpenAPI schema at /api/schema/
- [x] Archived old/outdated documentation

### Code Quality ✅
- [x] All 5 automated tests passing
- [x] No linting errors
- [x] Code follows PEP 8 standards
- [x] Comprehensive error handling
- [x] Input validation on all endpoints
- [x] SQL injection protection (Django ORM)
- [x] XSS protection enabled

### Database ✅
- [x] PostgreSQL configured
- [x] All migrations applied (40+ migrations)
- [x] 21 tables created successfully
- [x] Foreign key relationships established
- [x] Database indexes optimized
- [x] Test database configured

### Security ✅
- [x] JWT authentication implemented
- [x] Token blacklisting on logout
- [x] Password hashing (PBKDF2)
- [x] CORS configured
- [x] CSRF protection enabled
- [x] Permission classes on all views
- [x] Rate limiting ready (config available)

### API Functionality ✅
- [x] 45+ endpoints implemented
- [x] Authentication endpoints (10)
- [x] Movie endpoints (10)
- [x] Favorites & ratings (12)
- [x] Recommendations (3)
- [x] Health checks (3)
- [x] Pagination enabled
- [x] Filtering and search working

### Testing ✅
- [x] Unit tests written
- [x] Integration tests passing
- [x] Health check tests passing
- [x] User registration test passing
- [x] Test database configured
- [x] All 5 tests passing

### Monitoring ✅
- [x] Health check endpoint (/api/v1/health/)
- [x] Liveness probe (/api/v1/health/liveness/)
- [x] Readiness probe (/api/v1/health/readiness/)
- [x] Database connectivity check

---

## 🔧 Production Configuration Needed

### Required Environment Variables
```bash
# Critical - Must be configured before deployment
DJANGO_SECRET_KEY=<generate-new-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=<strong-unique-password>
TMDB_API_KEY=<valid-tmdb-api-key>
```

### Security Settings to Enable
```python
# In settings.py or environment
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_CONTENT_TYPE_NOSNIFF=True
```

### Recommended Production Enhancements
- [ ] Setup Redis for caching (replace LocMemCache)
- [ ] Configure production email backend (SMTP)
- [ ] Enable rate limiting on endpoints
- [ ] Setup Sentry for error tracking
- [ ] Configure automated database backups
- [ ] Setup monitoring/logging service
- [ ] Configure static file serving (WhiteNoise or S3)
- [ ] Setup HTTPS/SSL certificates

---

## 🗄️ Database Setup (Production)

### PostgreSQL Production Setup

```bash
# 1. Create production database
sudo -u postgres psql
CREATE DATABASE nexus_db;
CREATE USER nexus_user WITH PASSWORD 'strong-unique-password';
ALTER ROLE nexus_user SET client_encoding TO 'utf8';
ALTER ROLE nexus_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE nexus_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE nexus_db TO nexus_user;
\q

# 2. Run migrations
python manage.py migrate

# 3. Create superuser
python manage.py createsuperuser

# 4. Collect static files
python manage.py collectstatic --noinput
```

### Backup Strategy
```bash
# Automated daily backups
pg_dump -U nexus_user nexus_db > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -U nexus_user nexus_db < backup_20260211.sql
```

---

## 🚀 Deployment Options

### Option 1: Traditional VPS (DigitalOcean, Linode, etc.)

**Requirements**:
- Ubuntu 22.04 LTS or later
- 2GB RAM minimum (4GB recommended)
- PostgreSQL 15+
- Python 3.11+
- Nginx as reverse proxy
- Gunicorn as WSGI server

**Steps**:
```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql nginx

# 2. Clone repository
git clone <your-repo-url>
cd alx-project-nexus

# 3. Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with production values

# 5. Setup database
sudo -u postgres psql < setup_db.sql

# 6. Run migrations
python manage.py migrate
python manage.py collectstatic

# 7. Setup Gunicorn
pip install gunicorn
gunicorn movie_backend.wsgi:application --bind 0.0.0.0:8000

# 8. Configure Nginx (see nginx config below)
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### Option 2: Heroku

**Requirements**:
- Heroku account
- Heroku CLI installed

**Steps**:
```bash
# 1. Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. Login and create app
heroku login
heroku create alx-movie-api

# 3. Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# 4. Set environment variables
heroku config:set DJANGO_SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set TMDB_API_KEY="your-tmdb-key"

# 5. Deploy
git push heroku main

# 6. Run migrations
heroku run python manage.py migrate
heroku run python manage.py createsuperuser

# 7. Open app
heroku open
```

**Required Files**:
- `Procfile`: `web: gunicorn movie_backend.wsgi`
- `runtime.txt`: `python-3.11.14`

---

### Option 3: AWS (EC2 + RDS)

**Requirements**:
- AWS account
- EC2 instance (t2.small or larger)
- RDS PostgreSQL instance

**High-Level Steps**:
1. Launch EC2 instance with Ubuntu 22.04
2. Create RDS PostgreSQL database
3. Configure security groups (allow port 80, 443, 5432)
4. SSH into EC2 and follow VPS deployment steps
5. Update .env with RDS database credentials
6. Configure Route 53 for DNS
7. Setup SSL with Let's Encrypt

---

### Option 4: Railway.app

**Requirements**:
- Railway account
- GitHub repository

**Steps**:
1. Connect GitHub repository to Railway
2. Add PostgreSQL database plugin
3. Configure environment variables
4. Deploy automatically on push
5. Railway handles SSL and domain

---

## 🧪 Pre-Deployment Testing

### 1. Run All Tests
```bash
python manage.py test
# Expected: Ran 5 tests in X.XXXs - OK
```

### 2. Check Migrations
```bash
python manage.py makemigrations --check --dry-run
# Expected: No changes detected
```

### 3. Test Health Endpoints
```bash
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/health/liveness/
curl http://localhost:8000/api/v1/health/readiness/
# Expected: 200 OK responses
```

### 4. Validate Static Files
```bash
python manage.py collectstatic --dry-run
# Check for errors
```

### 5. Test with DEBUG=False
```bash
# Set DEBUG=False in .env
python manage.py runserver
# Test all endpoints - ensure no errors
```

---

## 📊 Post-Deployment Verification

### 1. Health Checks
```bash
curl https://yourdomain.com/api/v1/health/
curl https://yourdomain.com/api/v1/health/readiness/
```

### 2. API Documentation
- Visit: https://yourdomain.com/api/docs/
- Verify Swagger UI loads
- Test authentication endpoints

### 3. Database Connectivity
```bash
# Login to admin
https://yourdomain.com/admin/
# Verify all models visible
```

### 4. Monitoring Setup
- [ ] Check health endpoint every 5 minutes
- [ ] Monitor database connections
- [ ] Track API response times
- [ ] Setup error alerting
- [ ] Monitor disk space
- [ ] Check SSL certificate expiry

---

## 🔒 Security Checklist (Production)

### Application Security
- [ ] DEBUG=False
- [ ] Strong SECRET_KEY (50+ characters)
- [ ] ALLOWED_HOSTS configured
- [ ] SECURE_SSL_REDIRECT=True
- [ ] SESSION_COOKIE_SECURE=True
- [ ] CSRF_COOKIE_SECURE=True
- [ ] SECURE_HSTS_SECONDS configured
- [ ] Admin URL changed from /admin/

### Database Security
- [ ] Strong database password
- [ ] Database not publicly accessible
- [ ] Regular automated backups
- [ ] Backup retention policy
- [ ] Point-in-time recovery enabled

### Infrastructure Security
- [ ] SSH key authentication (no password)
- [ ] Firewall configured (ufw/security groups)
- [ ] Only ports 80, 443, 22 open
- [ ] SSL/TLS certificates installed
- [ ] Regular security updates scheduled
- [ ] Root login disabled
- [ ] Non-root user for Django app

### API Security
- [ ] Rate limiting enabled
- [ ] JWT tokens with expiry
- [ ] Token blacklisting working
- [ ] CORS origins restricted
- [ ] Input validation on all endpoints
- [ ] Error messages don't leak info

---

## 📝 Environment Variables Reference

### Required
```bash
DJANGO_SECRET_KEY=<50-char-random-string>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=nexus_db
DB_USER=nexus_user
DB_PASSWORD=<strong-password>
DB_HOST=localhost  # or RDS endpoint
DB_PORT=5432
TMDB_API_KEY=<valid-tmdb-key>
```

### Optional but Recommended
```bash
CORS_ALLOWED_ORIGINS=https://yourdomain.com
CACHE_BACKEND=django_redis.cache.RedisCache
REDIS_URL=redis://localhost:6379/1
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
```

---

## 🎯 Success Criteria

Deployment is successful when:
- ✅ All health checks return 200 OK
- ✅ Swagger UI loads at /api/docs/
- ✅ User can register and login
- ✅ Movies endpoint returns data
- ✅ Favorites/ratings work
- ✅ Recommendations generate
- ✅ Admin panel accessible
- ✅ HTTPS working (no mixed content)
- ✅ Database backups configured
- ✅ Monitoring/alerting active

---

## 🆘 Troubleshooting

### Issue: Static files not loading
**Solution**:
```bash
python manage.py collectstatic --noinput
# Configure WhiteNoise or serve via Nginx
```

### Issue: Database connection failed
**Solution**:
```bash
# Check credentials in .env
# Verify PostgreSQL running: sudo systemctl status postgresql
# Check firewall rules
# Test connection: psql -U nexus_user -d nexus_db -h localhost
```

### Issue: 400 Bad Request
**Solution**:
```bash
# Check ALLOWED_HOSTS in settings
# Verify CSRF_TRUSTED_ORIGINS
# Check CORS_ALLOWED_ORIGINS
```

### Issue: 500 Internal Server Error
**Solution**:
```bash
# Check logs: tail -f /var/log/django/error.log
# Enable detailed errors temporarily
# Check Sentry for error details
```

---

## 📞 Support

- **Documentation**: /docs/README.md
- **API Docs**: /api/docs/
- **Health Status**: /api/v1/health/
- **Admin**: /admin/

---

## 🎉 Final Checklist

Before going live:
- [ ] All tests passing
- [ ] Documentation reviewed
- [ ] Environment variables configured
- [ ] Database backups tested
- [ ] SSL certificate installed
- [ ] Monitoring configured
- [ ] Error tracking setup (Sentry)
- [ ] Performance tested (load testing)
- [ ] Security audit completed
- [ ] Backup/recovery tested
- [ ] Team trained on deployment

---

**Ready to deploy!** 🚀

**Last Updated**: February 11, 2026
**Next Review**: Before production launch

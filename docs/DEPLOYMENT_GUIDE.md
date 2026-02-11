# 🚀 Deployment Checklist

## Pre-Deployment Setup

### 1. Environment Variables
Create/update `.env` file with:
```bash
# Django
DJANGO_SECRET_KEY=your-super-secret-key-here
DEBUG=True  # Set to False in production

# Database
DB_NAME=nexus_db
DB_USER=nexus
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

# TMDb API
TMDB_API_KEY=your-tmdb-api-key-here

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

### 2. Get TMDb API Key
1. Go to https://www.themoviedb.org/
2. Sign up for free account
3. Go to Settings → API
4. Request API key (choose Developer option)
5. Copy the API Key (v3 auth)
6. Add to `.env` file

### 3. Database Setup (PostgreSQL)
```bash
# Option 1: Use existing nexus_db
# If you already have the database from Phase 0

# Option 2: Create new database
sudo -u postgres psql
CREATE DATABASE nexus_db;
CREATE USER nexus WITH PASSWORD 'your-password';
ALTER ROLE nexus SET client_encoding TO 'utf8';
ALTER ROLE nexus SET default_transaction_isolation TO 'read committed';
ALTER ROLE nexus SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE nexus_db TO nexus;
\q
```

---

## Quick Start (fyp_env)

### Step 1: Activate Environment
```bash
mamba activate fyp_env
```

### Step 2: Install Dependencies
```bash
cd /home/jalloh/Desktop/ALL/ALX_SE/alx-project-nexus
pip install -r requirements.txt
```

### Step 3: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --run-syncdb  # If needed
```

### Step 4: Create Superuser
```bash
python manage.py createsuperuser
# Email: admin@example.com
# Password: (choose a strong password)
```

### Step 5: Sync Genres from TMDb
```bash
# Start server first
python manage.py runserver

# In another terminal:
curl -X POST http://localhost:8000/api/v1/movies/genres/sync/
```

### Step 6: Test the API
```bash
# Register a user
curl -X POST http://localhost:8000/api/v1/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "ikdiallotechie@gmail.com",
    "password": "TestPass123",
    "password_confirm": "TestPass123"
  }'

# Login (save the access token)
curl -X POST http://localhost:8000/api/v1/auth/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'

# Get trending movies (no auth needed)
curl http://localhost:8000/api/v1/movies/movies/trending/
```

---

## Verification Checklist

### ✅ API Endpoints Working
- [ ] User registration
- [ ] User login returns JWT tokens
- [ ] Trending movies returns TMDb data
- [ ] Search movies works
- [ ] Can add movies to favorites (with auth)
- [ ] Can rate movies (with auth)
- [ ] Recommendations are generated (with auth)

### ✅ Documentation Accessible
- [ ] Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- [ ] ReDoc: http://localhost:8000/api/schema/redoc/
- [ ] Admin panel: http://localhost:8000/admin/

### ✅ Database
- [ ] All migrations applied successfully
- [ ] Tables created (users, movies, genres, etc.)
- [ ] Can create superuser
- [ ] Genres synced from TMDb

### ✅ TMDb Integration
- [ ] API key configured in .env
- [ ] Trending movies endpoint returns data
- [ ] Search returns relevant movies
- [ ] Genres sync successfully

---

## Common Issues & Solutions

### Issue: ModuleNotFoundError
**Solution:** Install missing packages
```bash
pip install djangorestframework djangorestframework-simplejwt psycopg2-binary django-cors-headers drf-spectacular requests python-decouple django-filter
```

### Issue: Database connection error
**Solution:** Check PostgreSQL is running and credentials are correct
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql  # if not running
```

### Issue: TMDb API returns empty results
**Solution:**
1. Verify API key is correct in .env
2. Check TMDb API status: https://status.themoviedb.org/
3. Ensure TMDB_API_KEY is loaded: `python manage.py shell` → `from django.conf import settings` → `print(settings.TMDB_API_KEY)`

### Issue: Migrations fail
**Solution:**
```bash
# Reset migrations (CAUTION: Deletes data)
python manage.py migrate --fake favorites zero
python manage.py migrate --fake movies zero
python manage.py migrate --fake recommendations zero
python manage.py migrate --fake users zero

# Re-run migrations
python manage.py makemigrations
python manage.py migrate
```

---

## Testing the Complete Flow

### 1. Register & Login
```bash
# Register
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"ikdiallotechie@gmail.com","password":"DemoPass123","password_confirm":"DemoPass123"}')

echo $REGISTER_RESPONSE | jq

# Extract access token
ACCESS_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.tokens.access')
echo "Access Token: $ACCESS_TOKEN"
```

### 2. Browse Movies
```bash
# Trending
curl http://localhost:8000/api/v1/movies/movies/trending/ | jq

# Search
curl "http://localhost:8000/api/v1/movies/movies/search/?q=batman" | jq

# Popular
curl http://localhost:8000/api/v1/movies/movies/popular/ | jq
```

### 3. Add Favorites & Ratings
```bash
# Add to favorites (assuming movie ID 1 exists in DB)
curl -X POST http://localhost:8000/api/v1/favorites/favorites/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"movie": 1}' | jq

# Rate a movie
curl -X POST http://localhost:8000/api/v1/favorites/ratings/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"movie": 1, "rating": 9}' | jq
```

### 4. Get Recommendations
```bash
curl http://localhost:8000/api/v1/recommendations/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

---

## Performance Optimization (Optional)

### Enable Redis Caching
```bash
# Install Redis
sudo apt install redis-server  # Ubuntu/Debian
brew install redis  # macOS

# Start Redis
redis-server

# Update settings.py CACHES configuration (already done)
```

### Database Optimization
```bash
# Create indexes (if needed)
python manage.py dbshell
CREATE INDEX idx_movies_tmdb_id ON movies(tmdb_id);
CREATE INDEX idx_movies_popularity ON movies(popularity DESC);
```

---

## Ready for Frontend Integration

Your backend is now fully functional! Provide frontend developers with:
1. **Base URL:** `http://localhost:8000/api/v1/`
2. **Swagger Docs:** `http://localhost:8000/api/schema/swagger-ui/`
3. **API Quick Reference:** `API_QUICK_REFERENCE.md`
4. **Authentication:** JWT tokens in `Authorization: Bearer <token>` header

---

## Next Steps

1. ✅ **Test all endpoints manually**
2. ✅ **Review Swagger documentation**
3. ✅ **Share API docs with frontend team**
4. 🔄 **Deploy to production (Railway/Render/AWS)**
5. 🔄 **Set up monitoring and logging**
6. 🔄 **Configure HTTPS/SSL**
7. 🔄 **Set up automated backups**

---

**🎉 Congratulations! Your movie recommendation backend is complete and ready to use!**

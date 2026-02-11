# Getting Started - Movie Recommendation API

## 🎯 Quick Start Guide

This guide will help you get the Movie Recommendation API up and running in **under 10 minutes**.

---

## ✅ Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed ([Download](https://www.python.org/downloads/))
- **PostgreSQL 15+** installed ([Download](https://www.postgresql.org/download/))
- **Git** installed ([Download](https://git-scm.com/downloads))
- **TMDb API Key** ([Get Free Key](https://www.themoviedb.org/settings/api))

### Verify Installations

```bash
python --version  # Should show Python 3.11+
psql --version    # Should show PostgreSQL 15+
git --version     # Should show Git 2.x+
```

---

## 🚀 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/jalloh19/alx-project-nexus.git
cd alx-project-nexus
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate          # On Linux/Mac
# OR
venv\Scripts\activate             # On Windows
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected packages** (19 total):
- Django 5.2.7
- djangorestframework 3.16.1
- djangorestframework-simplejwt 5.5.1
- psycopg2-binary 2.9.11
- drf-spectacular 0.29.0
- And more...

### 4. Setup PostgreSQL Database

```bash
# Method 1: Using createdb command
createdb nexus_db

# Method 2: Using psql
psql -U postgres
CREATE DATABASE nexus_db;
\q

# Create database user (optional but recommended)
createuser nexus_user -P
# Enter password when prompted

# Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE nexus_db TO nexus_user;"
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example file
cp .env.example .env

# Edit with your settings
nano .env  # or use your preferred editor
```

**Required .env contents:**

```bash
# Django
DJANGO_SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=nexus_db
DB_USER=nexus_user
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

# TMDb API
TMDB_API_KEY=your_tmdb_api_key_here

# JWT (Optional - defaults work fine)
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7
```

**Get TMDb API Key:**
1. Go to https://www.themoviedb.org/signup
2. Create account and verify email
3. Go to Settings → API → Create API Key
4. Choose "Developer" option
5. Fill in the application details
6. Copy your API key to `.env`

### 6. Run Database Migrations

```bash
python manage.py migrate
```

**Expected output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, favorites, movies, recommendations, sessions, token_blacklist, users
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying users.0001_initial... OK
  ...
  (21 tables created successfully)
```

### 7. Create Superuser (Optional but Recommended)

```bash
python manage.py createsuperuser
```

Enter:
- Email: admin@example.com
- Username: admin
- Password: (choose a strong password)

### 8. Run Development Server

```bash
python manage.py runserver
```

**You should see:**
```
System check identified no issues (0 silenced).
February 11, 2026 - 10:00:00
Django version 5.2.7, using settings 'movie_backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## ✨ Verify Installation

### 1. Check API Health

Open your browser or use curl:

```bash
curl http://localhost:8000/health/
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": true,
  "timestamp": "2026-02-11T10:00:00.000000Z"
}
```

### 2. Access Swagger Documentation

Open in browser: http://localhost:8000/api/docs/

You should see the interactive Swagger UI with all API endpoints.

### 3. Access Admin Panel

Open in browser: http://localhost:8000/admin/

Login with the superuser credentials you created.

### 4. Test Authentication Endpoint

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Expected response (201 Created):**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User",
  "full_name": "Test User",
  "is_verified": false,
  "date_joined": "2026-02-11T10:00:00Z",
  "profile": {...}
}
```

---

## 📚 Next Steps

### 1. Explore the API

Visit the **Swagger UI** at http://localhost:8000/api/docs/ to:
- View all 45+ endpoints
- Test endpoints interactively
- See request/response schemas
- Understand authentication flow

### 2. Run Tests

```bash
# Run all tests
python manage.py test

# Run with verbosity
python manage.py test --verbosity=2

# Run specific app tests
python manage.py test apps.users
python manage.py test apps.core
```

**Expected output:**
```
Found 5 test(s).
...
Ran 5 tests in 1.0s
OK
```

### 3. Load Sample Data (Optional)

```bash
# Create some test movies manually via Django shell
python manage.py shell

>>> from apps.movies.models import Movie, Genre
>>> genre = Genre.objects.create(tmdb_id=28, name="Action")
>>> movie = Movie.objects.create(
...     tmdb_id=603,
...     title="The Matrix",
...     overview="A computer hacker learns...",
...     release_date="1999-03-30",
...     vote_average=8.7,
...     popularity=78.5
... )
>>> movie.genres.add(genre)
>>> exit()
```

### 4. Make Your First API Call

```bash
# Get trending movies (requires TMDb API key configured)
curl http://localhost:8000/api/v1/movies/trending/

# Search for movies
curl "http://localhost:8000/api/v1/movies/search/?q=matrix"

# Get genres
curl http://localhost:8000/api/v1/movies/genres/
```

---

## 🔧 Common Issues & Solutions

### Issue: `psycopg2` installation fails

**Solution:**
```bash
# On Ubuntu/Debian
sudo apt-get install python3-dev libpq-dev

# On Mac with Homebrew
brew install postgresql

# Then reinstall
pip install psycopg2-binary
```

### Issue: Database connection refused

**Solution:**
1. Check PostgreSQL is running: `sudo service postgresql status`
2. Start if needed: `sudo service postgresql start`
3. Verify connection: `psql -U postgres -c "\l"`
4. Check credentials in `.env` file

### Issue: Migrations fail

**Solution:**
```bash
# Reset migrations (development only!)
python manage.py migrate --fake-initial

# Or start fresh
dropdb nexus_db
createdb nexus_db
python manage.py migrate
```

### Issue: TMDb API returns empty results

**Solution:**
1. Verify API key is correct in `.env`
2. Check TMDb account is activated
3. Test API key: `curl "https://api.themoviedb.org/3/movie/popular?api_key=YOUR_KEY"`

### Issue: Port 8000 already in use

**Solution:**
```bash
# Find process using port
lsof -i :8000  # On Linux/Mac
netstat -ano | findstr :8000  # On Windows

# Kill process or use different port
python manage.py runserver 8001
```

---

## 📁 Project Structure Overview

```
alx-project-nexus/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .env.example          # Environment template
│
├── movie_backend/        # Main Django project
│   ├── settings.py       # Django settings
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py           # WSGI application
│
├── api/v1/               # API version 1
│   └── urls.py           # API routing
│
├── apps/                 # Django applications
│   ├── core/            # Health checks, utilities
│   ├── users/           # Authentication, profiles
│   ├── movies/          # Movie data, TMDb integration
│   ├── favorites/       # Favorites, ratings
│   └── recommendations/ # ML recommendations
│
└── docs/                # Documentation
```

---

## 🎓 Learning Resources

### API Endpoints

- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Admin Panel**: http://localhost:8000/admin/

### Documentation Files

- `README.md` - Full project documentation
- `API_QUICK_REFERENCE.md` - Quick endpoint reference
- `DEPLOYMENT_GUIDE.md` - Production deployment guide

### Django Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)

---

## ✅ Verification Checklist

Before moving forward, ensure:

- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list` shows 19+ packages)
- [ ] PostgreSQL running and database created
- [ ] `.env` file created with all required variables
- [ ] Migrations completed successfully (21 tables)
- [ ] Superuser created
- [ ] Development server running
- [ ] Health check returns `"status": "healthy"`
- [ ] Swagger UI accessible
- [ ] Admin panel accessible
- [ ] All tests passing (`python manage.py test`)

---

## 🎉 You're Ready!

Your Movie Recommendation API is now running!

**Next Steps:**
1. Explore the Swagger UI
2. Test authentication endpoints
3. Try movie search and recommendations
4. Review the main README.md for advanced features
5. Check out the deployment guide for production setup

**Happy Coding! 🚀**

---

## 💡 Tips

- Use **Postman** or **Insomnia** for easier API testing
- Enable **Django Debug Toolbar** for development insights
- Check **logs** if something doesn't work
- Use `python manage.py shell` for quick database queries
- Commit your `.env.example` but **never** commit `.env`

---

## 📞 Need Help?

- Check the main `README.md` for detailed documentation
- Review error messages carefully
- Search GitHub issues
- Check Django and DRF documentation
- Ask on Stack Overflow with `django` and `django-rest-framework` tags

---

**Made with ❤️ for ALX Students**

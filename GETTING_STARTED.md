# Getting Started - Movie Recommendation System

## ✅ What We Built

A **simplified Django REST API** structure for local development:
- Single `settings.py` file (no environment splits)
- SQLite database (no PostgreSQL setup needed)
- REST API with DRF (no GraphQL, no Celery)
- Clean, modular app structure

## 📁 Current Structure

```
alx-project-nexus/
├── manage.py
├── requirements.txt (simplified)
├── movie_backend/
│   ├── settings.py (single file - easy!)
│   ├── urls.py
│   └── wsgi.py
├── api/v1/
│   └── urls.py (API routing)
└── apps/
    ├── core/         (utilities, health checks)
    ├── users/        (authentication)
    ├── movies/       (movie data)
    ├── favorites/    (user interactions)
    └── recommendations/  (ML - to implement)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables

Create `.env` file:
```bash
DJANGO_SECRET_KEY=your-secret-key-here
TMDB_API_KEY=your-tmdb-api-key
DEBUG=True
```

### 3. Initialize Database

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Visit:
- **API Docs**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/health/

## 📝 Next Steps

### To Complete (in order):

1. **Complete Movies App**
   - Add serializers, views, URLs
   - Integrate TMDb API client

2. **Complete Favorites App**
   - Move Favorite, Rating models from movies
   - Create serializers & views

3. **Complete Recommendations App**
   - Implement basic recommendation logic
   - Add ML algorithms later

4. **Add Features**
   - User authentication endpoints
   - Movie search & filtering
   - Recommendation generation

## 🏗️ Architecture Decisions

- ✅ **REST API** (not GraphQL) - simpler, better caching
- ✅ **SQLite** (not PostgreSQL) - easy local development
- ✅ **No Celery** (for now) - add when needed for ML
- ✅ **No Redis** (for now) - optimize later
- ✅ **Single settings file** - deploy complexity later

## 📚 Key Files

- `movie_backend/settings.py` - All configuration
- `api/v1/urls.py` - API routing
- `apps/users/models.py` - User & UserProfile
- `apps/movies/models.py` - Movie, Genre
- `apps/favorites/models.py` - Favorite, Rating, WatchHistory

## 🎯 API Endpoints (Planned)

```
POST   /api/v1/auth/register/
POST   /api/v1/auth/login/
GET    /api/v1/auth/me/

GET    /api/v1/movies/
GET    /api/v1/movies/{id}/
GET    /api/v1/movies/trending/
GET    /api/v1/movies/search/?q=...

GET    /api/v1/favorites/
POST   /api/v1/favorites/
DELETE /api/v1/favorites/{id}/

GET    /api/v1/recommendations/
```

## 🔧 Commands

```bash
# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Run tests (when written)
pytest
```

## 📖 What Changed from Original

**Removed (for simplicity):**
- ❌ Celery configuration
- ❌ Redis caching
- ❌ PostgreSQL (using SQLite)
- ❌ AWS S3 integration
- ❌ Production settings split
- ❌ Docker/Kubernetes configs

**These can be added later when deploying!**

**Kept (essential):**
- ✅ Django + DRF
- ✅ JWT Authentication
- ✅ Modular app structure
- ✅ API documentation
- ✅ User management
- ✅ Movie models

---

**Ready to start implementing! 🚀**

Focus on understanding the structure first, then build feature by feature.

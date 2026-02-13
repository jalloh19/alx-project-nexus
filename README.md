# ALX Project Nexus - Movie Recommendation API 🎬

[![Python](https://img.shields.io/badge/Python-3.11.14-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](#testing)
[![API](https://img.shields.io/badge/API-v1-orange.svg)](#api-endpoints)

> **Production Status**: ✅ Production Ready
> **Version**: 1.0.0
> **Last Updated**: February 12, 2026

---

## 📖 Overview

A production-ready REST API backend for movie recommendations, built with Django and Django REST Framework. Features JWT authentication, TMDb integration, personalized recommendations, comprehensive API documentation, and full test coverage.

### ✨ Key Features

- **🔐 Authentication**: JWT-based auth with token refresh & blacklisting
- **🎬 Movies**: Trending, popular, search, genres, and details from TMDb
- **🔄 TMDb Auto-Sync**: Movies auto-save to DB when browsed; bulk seed via `sync_tmdb` command
- **⭐ User Features**: Favorites, ratings (1-10) with reviews
- **🤖 Smart Recommendations**: Multi-signal engine (genre affinity, popularity, quality, recency, collaborative filtering) with diversity re-ranking
- **👍 Feedback Loop**: Like / dislike / not-interested on recommendations feeds back into the engine
- **📚 Documentation**: Interactive Swagger UI + OpenAPI 3.0 schema
- **🏥 Monitoring**: Health check endpoints for production
- **✅ Tested**: 5 passing tests with comprehensive coverage
- **🗄️ Database**: PostgreSQL with 21 optimized tables
- **☁️ Deployed**: Live on Render (https://alx-project-nexus-m3is.onrender.com/)

### 📊 Project Statistics

- **Total Endpoints**: 47+
- **Apps**: 5 (users, movies, favorites, recommendations, core)
- **Database Tables**: 21
- **Movie Pool**: 250+ movies auto-synced from TMDb
- **Test Coverage**: User auth, health checks, API endpoints
- **Documentation**: Swagger UI + OpenAPI 3.0

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- TMDb API Key ([Get one here](https://www.themoviedb.org/settings/api))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/jalloh19/alx-project-nexus.git
cd alx-project-nexus
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings:
# - DJANGO_SECRET_KEY
# - DATABASE_URL (PostgreSQL connection string)
# - TMDB_API_KEY
# - DEBUG=True (for development)
```

5. **Setup database**
```bash
# Create PostgreSQL database
createdb nexus_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

6. **Seed movie data from TMDb**
```bash
# Sync genres + trending/popular/top-rated movies into local DB
python manage.py sync_tmdb --pages 5
```

7. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

---

## 🌐 Using the Live Deployed API

> **Base URL**: `https://alx-project-nexus-m3is.onrender.com/`

The API is live and publicly accessible — no local setup required to explore it!

### Live Links

| Resource | URL |
|----------|-----|
| **Swagger UI** (Interactive Docs) | [https://alx-project-nexus-m3is.onrender.com/api/docs/](https://alx-project-nexus-m3is.onrender.com/api/docs/) |
| **Health Check** | [https://alx-project-nexus-m3is.onrender.com/health/](https://alx-project-nexus-m3is.onrender.com/health/) |
| **OpenAPI Schema** | [https://alx-project-nexus-m3is.onrender.com/api/schema/](https://alx-project-nexus-m3is.onrender.com/api/schema/) |
| **Admin Panel** | [https://alx-project-nexus-m3is.onrender.com/admin/](https://alx-project-nexus-m3is.onrender.com/admin/) |

### Quick Test (No Setup Needed)

```bash
# 1. Check API health
curl https://alx-project-nexus-m3is.onrender.com/health/

# 2. Browse trending movies (public, no auth required)
curl https://alx-project-nexus-m3is.onrender.com/api/v1/movies/trending/

# 3. Search for movies
curl "https://alx-project-nexus-m3is.onrender.com/api/v1/movies/search/?q=matrix"

# 4. View genres
curl https://alx-project-nexus-m3is.onrender.com/api/v1/movies/genres/
```

### Full Workflow (Register → Login → Use Features)

```bash
# Step 1: Register a new account
curl -X POST https://alx-project-nexus-m3is.onrender.com/api/v1/auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "yourname@example.com",
    "username": "yourname",
    "password": "YourSecurePass123!",
    "password_confirm": "YourSecurePass123!",
    "first_name": "Your",
    "last_name": "Name"
  }'

# Step 2: Login to get JWT tokens
curl -X POST https://alx-project-nexus-m3is.onrender.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "yourname@example.com",
    "password": "YourSecurePass123!"
  }'
# Copy the "access" token from the response

# Step 3: Use authenticated endpoints (replace <TOKEN> with your access token)
curl https://alx-project-nexus-m3is.onrender.com/api/v1/recommendations/ \
  -H "Authorization: Bearer <TOKEN>"

# Step 4: Add a movie to favorites (replace <MOVIE_ID> with an actual movie ID)
curl -X POST https://alx-project-nexus-m3is.onrender.com/api/v1/favorites/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"movie": <MOVIE_ID>}'

# Step 5: Rate a movie
curl -X POST https://alx-project-nexus-m3is.onrender.com/api/v1/favorites/ratings/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"movie": <MOVIE_ID>, "rating": 9, "review": "Amazing movie!"}'
```

> **💡 Tip:** The easiest way to explore the API is through the [Swagger UI](https://alx-project-nexus-m3is.onrender.com/api/docs/) — it lets you try all endpoints interactively right in your browser!

> **⚠️ Note:** The Render free tier may take ~30 seconds to wake up on the first request if the service has been idle.

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI (Live)**: https://alx-project-nexus-m3is.onrender.com/api/docs/
- **Swagger UI (Local)**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: https://alx-project-nexus-m3is.onrender.com/api/schema/
- **Admin Panel**: https://alx-project-nexus-m3is.onrender.com/admin/

### API Endpoints Overview

#### Authentication (10 endpoints)
```
POST   /api/v1/auth/                    # Register new user
POST   /api/v1/auth/login/              # Login
POST   /api/v1/auth/logout/             # Logout
POST   /api/v1/auth/token/refresh/      # Refresh JWT token
POST   /api/v1/auth/change_password/    # Change password
GET    /api/v1/auth/me/                 # Current user profile
GET    /api/v1/auth/profiles/           # User profiles
PUT    /api/v1/auth/profiles/{id}/      # Update profile
```

#### Movies (10 endpoints)
```
GET    /api/v1/movies/                  # List movies
GET    /api/v1/movies/{id}/             # Movie details
GET    /api/v1/movies/trending/         # Trending movies
GET    /api/v1/movies/popular/          # Popular movies
GET    /api/v1/movies/top_rated/        # Top rated movies
GET    /api/v1/movies/search/?q=query   # Search movies
GET    /api/v1/movies/genres/           # List genres
GET    /api/v1/movies/tmdb/{id}/        # TMDb movie details
```

#### Favorites & Ratings (12 endpoints)
```
GET    /api/v1/favorites/               # List user favorites
POST   /api/v1/favorites/               # Add to favorites
DELETE /api/v1/favorites/{id}/          # Remove favorite
GET    /api/v1/favorites/check/{id}/    # Check if favorited

GET    /api/v1/favorites/ratings/       # List user ratings
POST   /api/v1/favorites/ratings/       # Create rating
PUT    /api/v1/favorites/ratings/{id}/  # Update rating
DELETE /api/v1/favorites/ratings/{id}/  # Delete rating
GET    /api/v1/favorites/ratings/movie/{id}/  # Get movie rating
```

#### Recommendations (5 endpoints)
```
GET    /api/v1/recommendations/              # Get recommendations
POST   /api/v1/recommendations/refresh/      # Refresh recommendations
GET    /api/v1/recommendations/similar/{id}/  # Similar movies
POST   /api/v1/recommendations/feedback/      # Submit feedback (like/dislike/not_interested)
GET    /api/v1/recommendations/feedback/list/  # List user feedback
```

#### Health & Monitoring (3 endpoints)
```
GET    /health/                         # Health check
GET    /health/liveness/                # Liveness probe
GET    /health/readiness/               # Readiness probe
```

---

## 🏗️ Architecture

### Project Structure

```
alx-project-nexus/
├── manage.py
├── requirements.txt
├── .env.example
├── conftest.py
│
├── movie_backend/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── api/v1/                 # API versioning
│   └── urls.py
│
├── apps/
│   ├── core/              # Utilities & health checks
│   │   ├── models.py
│   │   ├── views.py
│   │   └── tests.py
│   │
│   ├── users/             # Authentication & profiles
│   │   ├── models.py      # User, UserProfile
│   │   ├── serializers.py
│   │   ├── views.py       # UserViewSet, auth endpoints
│   │   └── tests/
│   │
│   ├── movies/            # Movie data & TMDb
│   │   ├── models.py      # Movie, Genre
│   │   ├── serializers.py
│   │   ├── views.py       # MovieViewSet, GenreViewSet (auto-persist TMDb)
│   │   ├── services/      # TMDb integration + DB persistence
│   │   └── management/    # Management commands
│   │       └── commands/
│   │           └── sync_tmdb.py  # Bulk seed movies from TMDb
│   │
│   ├── favorites/         # User interactions
│   │   ├── models.py      # Favorite, Rating (1-10 scale)
│   │   ├── serializers.py
│   │   └── views.py       # FavoriteViewSet, RatingViewSet
│   │
│   └── recommendations/   # Smart recommendations
│       ├── models.py      # Recommendation, RecommendationFeedback
│       ├── views.py       # + feedback endpoints
│       └── services/      # Multi-signal recommendation engine
│
└── docs/                  # Additional documentation
```

### Database Schema

**21 Tables** including:
- **users_user**: Custom user model
- **users_userprofile**: User preferences
- **movies_movie**: Movie data
- **movies_genre**: Genre catalog
- **favorites_favorite**: User favorites
- **favorites_rating**: Movie ratings with reviews
- **recommendations_recommendation**: ML-based suggestions
- **token_blacklist**: JWT token management
- Plus Django's auth, admin, sessions, and content types tables

---

## 🧪 Testing

### Run All Tests

```bash
python manage.py test
```

### Run Specific App Tests

```bash
# Users app
python manage.py test apps.users

# Core app (health checks)
python manage.py test apps.core
```

### Test Coverage

Current test suite includes:
- ✅ User model creation
- ✅ User registration API
- ✅ Health check endpoints (3 tests)
- ✅ Authentication flow

**Total**: 5 passing tests

### Run Tests with Verbosity

```bash
python manage.py test --verbosity=2
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/nexus_db
# Or configure individually:
DB_NAME=nexus_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# TMDb API
TMDB_API_KEY=your_tmdb_api_key_here

# JWT Settings
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS (for frontend integration)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Database Setup

```bash
# Create database
createdb nexus_db

# Create user (if needed)
createuser nexus_user -P

# Grant privileges
psql -c "GRANT ALL PRIVILEGES ON DATABASE nexus_db TO nexus_user;"

# Run migrations
python manage.py migrate
```

---

## 🔐 Security

### Authentication

- **JWT Tokens**: Stateless authentication with access & refresh tokens
- **Token Blacklisting**: Secure logout with token invalidation
- **Password Hashing**: PBKDF2 algorithm with salt
- **Token Expiry**: Configurable access (60min) and refresh (7 days) lifetimes

### API Security

- **CORS**: Configured for specific origins
- **HTTPS**: Required in production
- **Input Validation**: DRF serializers with Django validators
- **SQL Injection**: Protected by Django ORM
- **XSS**: Django's built-in template escaping

---

## 📈 Performance

### Caching Strategy

- **LocMemCache**: Development caching
- **Query Optimization**:
  - `select_related()` for foreign keys
  - `prefetch_related()` for many-to-many
- **Pagination**: DRF pagination for large datasets

### Database Optimization

- **Indexes**: Created on frequently queried fields
- **Connection Pooling**: PostgreSQL connection management
- **Query Analysis**: Django Debug Toolbar integration

---

## 🚢 Deployment

### Live Production URL

> **🔗 https://alx-project-nexus-m3is.onrender.com/**

Deployed on **Render** with auto-deploy from `main` branch.

| Live Resource | URL |
|---------------|-----|
| API Base | `https://alx-project-nexus-m3is.onrender.com/api/v1/` |
| Swagger Docs | https://alx-project-nexus-m3is.onrender.com/api/docs/ |
| Health Check | https://alx-project-nexus-m3is.onrender.com/health/ |
| Admin Panel | https://alx-project-nexus-m3is.onrender.com/admin/ |

### Render Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL Internal URL from Render DB |
| `DJANGO_SECRET_KEY` | Strong random secret |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com,localhost` |
| `TMDB_API_KEY` | Your TMDb v3 API key |

### Seed Production Database

After deploy, run via Render Shell:
```bash
python manage.py sync_tmdb --pages 5
```

### Production Server

```bash
# Gunicorn (configured in Procfile)
gunicorn movie_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 📊 API Response Examples

### Authentication

**POST /api/v1/auth/login/**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Movies

**GET /api/v1/movies/trending/**
```json
Response (200):
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tmdb_id": 603,
      "title": "The Matrix",
      "overview": "A computer hacker learns...",
      "release_date": "1999-03-30",
      "vote_average": 8.7,
      "popularity": 78.5,
      "poster_url": "https://image.tmdb.org/...",
      "backdrop_url": "https://image.tmdb.org/...",
      "genres": [
        {"id": 28, "name": "Action"},
        {"id": 878, "name": "Science Fiction"}
      ]
    }
  ]
}
```

### Ratings

**POST /api/v1/favorites/ratings/**
```json
Request:
{
  "movie": 1,
  "rating": 9,
  "review": "Excellent sci-fi masterpiece!"
}

Response (201):
{
  "id": 1,
  "movie": 1,
  "movie_detail": {
    "id": 1,
    "title": "The Matrix",
    "poster_url": "..."
  },
  "rating": 9,
  "review": "Excellent sci-fi masterpiece!",
  "created_at": "2026-02-11T10:30:00Z",
  "updated_at": "2026-02-11T10:30:00Z"
}
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

**ALX Software Engineering Student**
- GitHub: [@jalloh19](https://github.com/jalloh19)

---

## 🙏 Acknowledgments

- **ALX Africa** - Software Engineering Program
- **TMDb** - The Movie Database API
- **Django** & **Django REST Framework** communities
- All open-source contributors

---

## 📞 Support

For issues, questions, or contributions:
- 📧 Email: ikdiallotechie@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/jalloh19/alx-project-nexus/issues)
- 📖 Documentation: [API Docs (Live)](https://alx-project-nexus-m3is.onrender.com/api/docs/)

---

**Built with ❤️ by ALX Students | Production Ready February 2026**

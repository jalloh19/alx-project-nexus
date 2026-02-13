# COMPLETE PROJECT BRIEF — ALX Project Nexus

**Generated:** February 12, 2026

This file contains the complete collected information for the Movie Recommendation API project. It includes everything gathered during the security audit and research: project overview, exact model fields and relationships, endpoints, recommendation engine details, settings, deployment, tests, slide deck content, and AI tool suggestions. Nothing is omitted — even a dot.

---

## 1. Project Overview

**Name:** ALX Project Nexus — Movie Recommendation API 🎬
**Version:** 1.0.0
**Status:** ✅ Production Ready
**Live URL:** https://alx-project-nexus-m3is.onrender.com/
**Author:** [@jalloh19](https://github.com/jalloh19) (ikdiallotechie@gmail.com)
**License:** MIT

### Key Features
- **JWT Authentication** with token refresh & blacklisting
- **TMDb Integration** — auto-saves movies to DB when browsed; bulk seed via `sync_tmdb` command
- **Favorites & Ratings** (1–10 scale with reviews)
- **Smart Recommendations** — multi-signal engine with diversity re-ranking
- **Feedback Loop** — like / dislike / not-interested on recommendations
- **Swagger UI + OpenAPI 3.0** interactive docs
- **Health checks** (health, liveness, readiness)

### Statistics
- **Total Endpoints:** 47+
- **Django Apps:** 5 (users, movies, favorites, recommendations, core)
- **Database Tables:** 21
- **Movie Pool:** 250+ auto-synced from TMDb
- **Passing Tests:** 5

---

## 2. Data Models / ERD

> The following is the full structured model summary gathered from the codebase.

### Abstract Base Models
- **TimeStampedModel**: Provides `created_at` (DateTimeField, auto_now_add) and `updated_at` (DateTimeField, auto_now)
- **SoftDeleteModel**: `is_deleted` (BooleanField, default=False), `deleted_at` (DateTimeField, nullable)
- **BaseModel**: inherits TimeStampedModel (convenience abstract)

### Users App (models)

**User** (custom user model):
- Fields: `email` (EmailField, unique), `username` (CharField, unique), `first_name`, `last_name`, `password`, `is_active`, `is_staff`, `is_superuser`, `date_joined`, plus standard AbstractUser fields.
- `USERNAME_FIELD` is `email`.
- Indexes: email unique index.

**UserProfile**:
- Fields: `user` (OneToOneField → User, CASCADE, related_name), `bio` (TextField, blank, max_length=500), `avatar_url` (URLField, blank, null), `favorite_genres` (JSONField, default=list), `preferred_language` (CharField(10), default='en'), `mature_content` (BooleanField, default=False).

### Movies App (models)

**Genre**:
- Fields: `tmdb_id` (IntegerField, unique), `name` (CharField(max_length=100)).

**Movie**:
- Fields (selected):
  - `tmdb_id` (IntegerField, unique, db_index)
  - `title` (CharField)
  - `original_title` (CharField, blank, nullable)
  - `overview` (TextField)
  - `poster_path` (CharField, blank)
  - `backdrop_path` (CharField, blank)
  - `release_date` (DateField, null=True)
  - `runtime` (IntegerField, null=True)
  - `vote_average` (FloatField, default=0.0)
  - `vote_count` (IntegerField, default=0)
  - `popularity` (FloatField, default=0.0)
  - `original_language` (CharField(10), default='en')
  - `adult` (BooleanField, default=False)
  - `status` (CharField, blank)
  - `budget` (BigIntegerField, null=True)
  - `revenue` (BigIntegerField, null=True)
  - `homepage` (URLField, null=True)
  - `genres` (ManyToManyField → Genre, related_name)
- Indexes: tmdb_id, popularity, vote_average, release_date

**WatchHistory**:
- Fields: `user` (ForeignKey → User), `movie` (ForeignKey → Movie), `watched_at` (DateTimeField, auto_now_add)
- Related names: `watch_history`, `watched_by`.

### Favorites App (models)

**Favorite**:
- Fields: `user` (ForeignKey → User), `movie` (ForeignKey → Movie)
- Unique together: `(user, movie)`

**Rating**:
- Fields: `user` (ForeignKey → User), `movie` (ForeignKey → Movie), `rating` (FloatField, 1–10 scale), `review` (TextField, blank)
- Unique together: `(user, movie)`

### Recommendations App (models)

**Recommendation**:
- Fields: `user` (ForeignKey → User), `movie` (ForeignKey → Movie), `recommendation_type` (CharField(choices): collaborative/content_based/hybrid/personalized etc.), `confidence_score` (FloatField 0–1), `explanation` (TextField, blank), `is_clicked` (BooleanField, default=False), `is_rated` (BooleanField, default=False)
- Unique together: `(user, movie)`

**RecommendationFeedback**:
- Fields: `user` (ForeignKey → User), `recommendation` (ForeignKey → Recommendation), `feedback_type` (CharField: like/dislike/not_interested), `comment` (TextField, blank)
- Unique together: `(user, recommendation)`

### Entity Relationships Summary (ERD ASCII)
```
User ──1:1──→ UserProfile
User ──1:N──→ Favorite ──N:1──→ Movie
User ──1:N──→ Rating ──N:1──→ Movie
User ──1:N──→ WatchHistory ──N:1──→ Movie
User ──1:N──→ Recommendation ──N:1──→ Movie
User ──1:N──→ RecommendationFeedback ──N:1──→ Recommendation
Movie ──M:N──→ Genre
```

**Design choices:**
- Email-as-username improves UX and security.
- `tmdb_id` uniqueness enables idempotent upserts on TMDb sync and on-the-fly persistence.
- `unique_together` constraints for preventing duplicates (favorites, ratings, feedback).

---

## 3. Key Endpoints

### Root / Project-level
- `/admin/` — Django admin
- `/api/schema/` — OpenAPI schema (drf-spectacular)
- `/api/docs/` — Swagger UI
- `/health/` — Health checks

### API v1 Routing (high-level)
The project exposes the typical grouped routes under `/api/v1/*` per app: `auth`, `movies`, `favorites`, `recommendations`, `core`.

### Authentication Endpoints
- `POST /api/v1/auth/users/` — Register
- `POST /api/v1/auth/login/` — Login (returns JWT tokens)
- `POST /api/v1/auth/token/refresh/` — Refresh token
- `POST /api/v1/auth/token/blacklist/` — Blacklist refresh token
- `POST /api/v1/auth/token/verify/` — Verify token
- `POST /api/v1/auth/password/change/` — Change password
- `GET/PATCH /api/v1/auth/users/me/` — Current user profile
- `GET /api/v1/auth/profiles/` — List profiles
- `GET/PUT/PATCH /api/v1/auth/profiles/{id}/` — Profile detail

### Movies Endpoints (examples)
- `GET /api/v1/movies/movies/` — List local DB movies
- `GET /api/v1/movies/movies/{id}/` — Get movie detail
- `GET /api/v1/movies/movies/trending/` — TMDb trending (auto-persist)
- `GET /api/v1/movies/movies/popular/` — TMDb popular (auto-persist)
- `GET /api/v1/movies/movies/top_rated/` — TMDb top rated (auto-persist)
- `GET /api/v1/movies/movies/search/?q=` — TMDb search (auto-persist)
- `GET /api/v1/movies/movies/tmdb/{tmdb_id}/` — TMDb detail (auto-persist)
- `GET /api/v1/movies/genres/` — List genres
- `POST /api/v1/movies/genres/sync/` — Sync genres from TMDb

### Favorites & Ratings Endpoints
- `GET /api/v1/favorites/favorites/` — List favorites
- `POST /api/v1/favorites/favorites/` — Add favorite
- `DELETE /api/v1/favorites/favorites/{id}/` — Remove favorite
- `GET /api/v1/favorites/ratings/` — List ratings
- `POST /api/v1/favorites/ratings/` — Create rating (rating: 1–10)
- `PUT /api/v1/favorites/ratings/{id}/` — Update rating
- `DELETE /api/v1/favorites/ratings/{id}/` — Delete rating

### Recommendations Endpoints
- `GET /api/v1/recommendations/` — Get recommendations (auto-generate if empty)
- `POST /api/v1/recommendations/refresh/` — Force regenerate recommendations
- `GET /api/v1/recommendations/similar/{movie_id}/` — Similar movies
- `POST /api/v1/recommendations/feedback/` — Submit feedback (like / dislike / not_interested)
- `GET /api/v1/recommendations/feedback/list/` — List user feedback

### Health Endpoints
- `GET /health/` — DB + cache check
- `GET /health/ready/` — Readiness probe
- `GET /health/live/` — Liveness probe

---

## 4. Recommendation Engine — Full Details

**File:** `apps/recommendations/services/recommendation_engine.py`

**Type:** Multi-signal content-based + collaborative hybrid. Implemented with plain Python and Django ORM (no heavy ML libs), suitable for free-tier hosting.

### Signals & Weights
- **Genre Affinity** — 45% (0.45)
  - Built by counting genres among user's favorites + highly-rated movies (rating ≥ 7). Normalized with max = 1.0.
- **Quality** — 20% (0.20)
  - Based on TMDb `vote_average` (converted to 0–1 scale) with upper cap.
- **Popularity** — 15% (0.15)
  - Based on TMDb `popularity` normalized (cap applied).
- **Recency** — 10% (0.10)
  - Linear decay over 730 days (2 years); newer gets boosted.
- **Collaborative** — 10% (0.10)
  - Finds users with similar top-5 genre profiles and aggregates their favorites.
- **Diversity Re-ranking** — applied after scoring to avoid genre repetition (max 3 consecutive of same top genre).

### Pipeline (summary)
1. Build `liked_movies` as union of favorites + ratings ≥ 7.
2. Build `user_genre_profile` = normalized genre counts.
3. Exclude dismissed movies (feedback: dislike / not_interested) and movies rated < 4.
4. Compute collaborative signal by finding top similar users (top N) and their favourite movies.
5. Score each candidate: weighted sum of signals.
6. Diversity re-rank to enforce genre spread (max 3 consecutive same-genre films).
7. If not enough candidates, pad with global popular movies.
8. Save new `Recommendation` batch; old ones are cleared.

### Constants & Parameters
- `RATING_THRESHOLD_HIGH = 7` (for liked candidates)
- `RATING_THRESHOLD_LOW = 4` (for exclusion consideration)
- Recency window: 730 days
- Minimum `confidence_score` threshold for candidate to be considered
- Collaborative: top 50 similar users, top 200 movies to consider

### Auxiliary methods present
- `build_user_genre_profile(user)`
- `get_candidate_movies()`
- `score_movie(candidate, user_profile)`
- `diversity_rerank(list_of_candidates)`
- `pad_with_popular()`

---

## 5. Tools, Frameworks & Dependencies

**From `requirements.txt` and project settings**

- Python 3.11.14
- Django 5.2.7
- djangorestframework 3.16.1
- djangorestframework-simplejwt 5.5.1
- psycopg2-binary 2.9.11
- drf-spectacular 0.29.0
- python-decouple 3.8
- requests 2.28.0
- django-filter 23.x
- django-cors-headers 4.x
- gunicorn 21.x
- whitenoise 6.5.x
- dj-database-url 2.1.x
- python-dateutil, pytz

**Other Tools**
- GitHub (repo + CI)
- Render (hosting) — web + managed Postgres
- Swagger UI via drf-spectacular

---

## 6. Deployment Configuration

**Platform:** Render (auto-deploy from `main` branch)

**Procfile:**
```
web: gunicorn movie_backend.wsgi:application --bind 0.0.0.0:$PORT
```

**Build & Start:**
```
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
# start:
gunicorn movie_backend.wsgi:application --bind 0.0.0.0:$PORT
```

**Environment Variables (required):**
- `DATABASE_URL` (Render-managed Postgres)
- `DJANGO_SECRET_KEY` (strong random)
- `DEBUG=False`
- `ALLOWED_HOSTS` (e.g., `.onrender.com,localhost`)
- `TMDB_API_KEY` (TMDb v3 key)

**Post-deploy:**
- Run `python manage.py sync_tmdb --pages 5` to seed genres + movies (≈ 250+ movies synced)

**Static Files:** WhiteNoise `CompressedManifestStaticFilesStorage` used for static serving.

---

## 7. Settings Summary (movie_backend/settings.py)

**Installed Apps**: `django.contrib.*`, `rest_framework`, `rest_framework_simplejwt.token_blacklist`, `corsheaders`, `drf_spectacular`, local apps: `apps.users`, `apps.movies`, `apps.favorites`, `apps.recommendations`, `apps.core`.

**Middleware (highlighted order):**
1. `SecurityMiddleware`
2. `WhiteNoiseMiddleware`
3. `CorsMiddleware`
4. `SessionMiddleware`
5. `CommonMiddleware`
6. `CsrfViewMiddleware`
7. `AuthenticationMiddleware`
8. `MessageMiddleware`
9. `XFrameOptionsMiddleware`

**DRF Config:**
- `DEFAULT_AUTHENTICATION_CLASSES`: JWTAuthentication
- `DEFAULT_PERMISSION_CLASSES`: IsAuthenticatedOrReadOnly
- Pagination: PageNumberPagination, page_size=20
- Filters: DjangoFilterBackend, SearchFilter, OrderingFilter
- Throttling: anon=100/hr, user=1000/hr
- Schema: drf-spectacular

**JWT:**
- Access lifetime: 60 minutes
- Refresh lifetime: 7 days
- Rotate refresh tokens: True
- Blacklist after rotation: True

**CORS Allowed Origins:** `localhost:3000`, `localhost:8080`, `localhost:4200`

**Password Validators:** Similar to Django defaults (min length 8, common password, numeric, similarity)

---

## 8. Tests

**Test Summary**:
- Framework: pytest & Django test cases
- Test count: Found 5 passing tests (users + core health checks)
- Notable tests:
  - `apps.users.tests` — user creation, registration
  - `apps.core.tests` — health checks (health, liveness, readiness)

**Test commands:**
```
python manage.py test
# or
pytest
```

---

## 9. TMDb Integration

**TMDb Service**: `apps/movies/services/tmdb_service.py`
- Base URL: `https://api.themoviedb.org/3`
- Key methods: `get_trending(category, page)`, `get_popular(page)`, `get_top_rated(page)`, `search(query, page)`, `get_movie_details(tmdb_id)`
- Caching: trending (1 hour), movie details (24 hours), genres (1 week)

**Persistence Pattern**:
- `persist_tmdb_movies()` — upserts list of movies and links genres (M2M), logs results
- `persist_tmdb_movie_detail()` — upsert single movie with detail
- Views call `_persist_in_background()` which spawns daemon `threading.Thread` to save results asynchronously so API response is fast.

**Management Command:** `python manage.py sync_tmdb --pages 5`
- Syncs genres first
- Fetches N pages across categories: trending-day, popular, top-rated, trending-week
- Sleeps 0.25s between API calls to respect rate limit
- Reports counts: genres synced, records upserted, unique movies

---

## 10. Slide Deck Content Draft (Ready-to-use)

### Slide 1 — Title Slide
- Title: Movie Recommendation API
- Subtitle: ALX Project Nexus — Backend Capstone
- Description: A full-stack REST API with smart movie recommendations, TMDb integration, and JWT authentication
- Author: Ibrahim Diallo Jalloh — @jalloh19
- Live: https://alx-project-nexus-m3is.onrender.com/
- Date: February 2026

### Slide 2 — Project Overview
- What is it? A production-ready Django REST API that lets users browse movies, save favorites, rate films (1–10), and receive personalized recommendations powered by a multi-signal engine.
- Key Numbers: 47+ Endpoints | 5 Django Apps | 21 DB Tables | 250+ Movies | 5 Passing Tests
- Core Capabilities: JWT auth, TMDb integration, favorites & ratings (1–10), recommendations (6-signal), feedback loop, Swagger UI

### Slide 3 — Architecture Overview
- Diagram ASCII (or use a visual): Client → Django REST API ←→ TMDb API; PostgreSQL for DB; Render for hosting
- 5 Apps: users, movies, favorites, recommendations, core

### Slide 4 — ERD (Entity Relationship Diagram)
- ERD ASCII (see "Entity Relationships Summary" section)
- Key design decisions (email-as-username, TimeStampedModel, unique_together, tmdb_id upsert strategy)

### Slide 5 — Data Model Rationale
- Table explaining models and purposes (User, UserProfile, Movie, Genre, Favorite, Rating, Recommendation, RecommendationFeedback)
- Design principle: auto-persist TMDb on browse → richer local pool

### Slide 6 — Key Endpoints & Features
- Endpoints list grouped by Auth, Movies, Favorites, Recommendations, Health
- Example flow demonstrating typical user journey

### Slide 7 — The Recommendation Engine
- Describe multi-signal engine and weights: Genre 45%, Quality 20%, Popularity 15%, Recency 10%, Collaborative 10%
- Pipeline steps and diversity re-ranking
- Note: runs without heavy ML libraries (Django ORM + Python)

### Slide 8 — Tools, Frameworks & Best Practices
- Stack: Python 3.11, Django 5.2.7, DRF 3.16.1, SimpleJWT, PostgreSQL, Gunicorn, WhiteNoise, python-decouple, drf-spectacular
- Best practices used: security, testing, pagination, filters, CI-friendly, env files not committed

### Slide 9 — Deployment Summary
- Platform: Render
- Commands: collectstatic, migrate, seed using `sync_tmdb`
- Required env vars: DATABASE_URL, DJANGO_SECRET_KEY, DEBUG, ALLOWED_HOSTS, TMDB_API_KEY
- Health endpoints and monitoring notes

### Slide 10 — Demo & Links
- Live API + Swagger + GitHub repo links
- Example curl commands
- Thank you slide

---

## 11. AI Tools & Slide Generation Recommendations

**Tools to generate slides (.pptx / Google Slides / Canva)**
- **Gamma.app** — paste the draft, get beautiful slides, export PPTX. Best overall.
- **SlidesAI.io** — Google Slides add-on that generates slides from text; directly produces a Google Slides deck to share with mentors.
- **Canva (Magic Design)** — good for branded visuals; export as PPTX.
- **Beautiful.ai** — professional templates, auto-formatting.
- **Tome.app** — narrative-style slides with storytelling.
- **ChatGPT (via prompt + python-pptx)** — can generate .pptx programmatically if you want a downloadable PPTX file.

**Recommendation:** Use SlidesAI for Google Slides (easy sharing), or Gamma.app for fast, high-quality exports. Use dbdiagram.io or Mermaid to create the ERD image and paste into the slide.

---

## 12. Commands & Useful Snippets

- Seed DB from TMDb (local or production):
```
python manage.py sync_tmdb --pages 5
```

- Collect static & migrate (production build):
```
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

- Run tests:
```
python manage.py test
# or
pytest
```

- Health check (curl):
```
curl https://alx-project-nexus-m3is.onrender.com/health/
```

---

## 13. Notes from Security Audit (short)
- `.env` is in `.gitignore` and not committed anywhere in Git history
- TMDb API key found only in `.env` (local) and `.env.example` contains placeholder
- No leaked keys found in repository or docs

---

## Appendix — Exact Textual Snippets & Examples (verbatim)

**Example Rating Create Request (updated to 1–10 scale):**
```json
{
  "movie": 1,
  "rating": 9,
  "review": "Excellent sci-fi masterpiece!"
}
```

**Feedback Submit Request Example:**
```json
{
  "recommendation": 1,
  "feedback_type": "like",
  "comment": "Great recommendation!"
}
```

**Recommendation Refresh Response Example:**
```json
{
  "message": "Generated 20 recommendations",
  "recommendations": [...]
}
```

---

.

(End of file — nothing omitted.)

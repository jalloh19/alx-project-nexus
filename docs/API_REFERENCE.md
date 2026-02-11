# API Quick Reference Guide

## Base URL
```
http://localhost:8000/api/v1
```

---

## 🔐 Authentication

All authenticated endpoints require JWT token in header:
```
Authorization: Bearer <access_token>
```

### Obtain Tokens

**POST** `/api/v1/auth/login/`

```json
Request:
{
  "email": "ikdiallotechie@gmail.com",
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

### Refresh Token

**POST** `/api/v1/auth/token/refresh/`

```json
Request:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (200):
{
  "access": "new_access_token_here"
}
```

---

## 👤 User Management

### Register New User

**POST** `/api/v1/auth/`

```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "StrongPass123!",
  "password_confirm": "StrongPass123!",
  "first_name": "New",
  "last_name": "User"
}
```

### Get Current User

**GET** `/api/v1/auth/me/` 🔒

### Change Password

**POST** `/api/v1/auth/change_password/` 🔒

```json
{
  "old_password": "OldPass123!",
  "new_password": "NewStrongPass123!",
  "new_password_confirm": "NewStrongPass123!"
}
```

### Logout

**POST** `/api/v1/auth/logout/` 🔒

```json
{
  "refresh": "refresh_token_to_blacklist"
}
```

---

## 🎬 Movies

### List/Search Movies

**GET** `/api/v1/movies/`

Query params:
- `search` - Search by title
- `ordering` - Sort field (e.g., `-popularity`, `release_date`)
- `page` - Page number for pagination

### Get Movie Details

**GET** `/api/v1/movies/{id}/`

### Trending Movies

**GET** `/api/v1/movies/trending/`

Query params:
- `time_window` - `day` or `week` (default: week)

### Popular Movies

**GET** `/api/v1/movies/popular/`

### Top Rated Movies

**GET** `/api/v1/movies/top_rated/`

### Search Movies

**GET** `/api/v1/movies/search/?q=matrix`

Required param: `q` or `query` - Search query

### Get TMDb Movie Details

**GET** `/api/v1/movies/tmdb/{tmdb_id}/`

### List Genres

**GET** `/api/v1/movies/genres/`

Response:
```json
[
  {"id": 28, "name": "Action"},
  {"id": 12, "name": "Adventure"},
  {"id": 878, "name": "Science Fiction"}
]
```

---

## ⭐ Favorites

All favorites endpoints require authentication 🔒

### List User Favorites

**GET** `/api/v1/favorites/`

### Add to Favorites

**POST** `/api/v1/favorites/`

```json
{
  "movie": 1
}
```

### Remove from Favorites

**DELETE** `/api/v1/favorites/{id}/`

### Check if Favorited

**GET** `/api/v1/favorites/check/{movie_id}/`

Response:
```json
{
  "is_favorited": true
}
```

---

## 📝 Ratings

All ratings endpoints require authentication 🔒

### List User Ratings

**GET** `/api/v1/favorites/ratings/`

### Create Rating

**POST** `/api/v1/favorites/ratings/`

```json
{
  "movie": 1,
  "rating": 4.5,
  "review": "Excellent movie! Highly recommended."
}
```

Note: Rating must be between 0.5 and 5.0 (increments of 0.5)

### Update Rating

**PUT/PATCH** `/api/v1/favorites/ratings/{id}/`

```json
{
  "rating": 5.0,
  "review": "Absolutely perfect!"
}
```

### Delete Rating

**DELETE** `/api/v1/favorites/ratings/{id}/`

### Get Rating for Specific Movie

**GET** `/api/v1/favorites/ratings/movie/{movie_id}/`

---

## 🤖 Recommendations

All recommendations endpoints require authentication 🔒

### Get Recommendations

**GET** `/api/v1/recommendations/`

Auto-generates recommendations if none exist.

### Refresh Recommendations

**POST** `/api/v1/recommendations/refresh/`

Force regenerate recommendations.

Response:
```json
{
  "message": "Generated 20 recommendations",
  "recommendations": [...]
}
```

### Get Similar Movies

**GET** `/api/v1/recommendations/similar/{movie_id}/`

---

## 🏥 Health Checks

### Main Health Check

**GET** `/health/`

```json
{
  "status": "healthy",
  "database": true,
  "timestamp": "2026-02-11T10:00:00Z"
}
```

### Liveness Probe

**GET** `/health/liveness/`

### Readiness Probe

**GET** `/health/readiness/`

---

## 📊 Response Formats

### Success Response (200)

```json
{
  "id": 1,
  "title": "The Matrix",
  ...
}
```

### Paginated Response

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/movies/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response (400)

```json
{
  "field_name": [
    "This field is required."
  ]
}
```

### Unauthorized (401)

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Not Found (404)

```json
{
  "detail": "Not found."
}
```

---

## 🔑 HTTP Status Codes

- **200** - Success
- **201** - Created
- **204** - No Content (successful deletion)
- **400** - Bad Request (validation error)
- **401** - Unauthorized (missing/invalid token)
- **403** - Forbidden (permission denied)
- **404** - Not Found
- **500** - Internal Server Error

---

## 📝 Example: Full User Flow

### 1. Register
```bash
curl -X POST http://localhost:8000/api/v1/auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "moviefan",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

Save the access token from response.

### 3. Get Trending Movies
```bash
curl http://localhost:8000/api/v1/movies/trending/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Add to Favorites
```bash
curl -X POST http://localhost:8000/api/v1/favorites/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"movie": 1}'
```

### 5. Rate Movie
```bash
curl -X POST http://localhost:8000/api/v1/favorites/ratings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "movie": 1,
    "rating": 4.5,
    "review": "Great movie!"
  }'
```

### 6. Get Recommendations
```bash
curl http://localhost:8000/api/v1/recommendations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔍 Advanced Queries

### Search with Filters
```
GET /api/v1/movies/?search=matrix&ordering=-popularity
```

### Pagination
```
GET /api/v1/favorites/?page=2
```

### Multiple Query Params
```
GET /api/v1/movies/search/?q=action&ordering=release_date
```

---

## 💡 Tips

- **Always include** `Content-Type: application/json` header for POST/PUT/PATCH
- **Access tokens expire** after 60 minutes (default)
- **Refresh tokens expire** after 7 days (default)
- **Use pagination** for large result sets
- **Check Swagger UI** for interactive testing: http://localhost:8000/api/docs/

---

**For detailed documentation, see:**
- Main README.md
- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI Schema: http://localhost:8000/api/schema/

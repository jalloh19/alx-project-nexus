# Complete Movie Recommendation API - Endpoints Reference

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication Endpoints

### Register
`POST /auth/users/`
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123"
}
```

### Login
`POST /auth/users/login/`
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

### Logout
`POST /auth/users/logout/`
```json
{
  "refresh": "refresh_token_here"
}
```

### Get Current User
`GET /auth/users/me/`

### Update Profile
`PATCH /auth/profiles/my_profile/`
```json
{
  "bio": "Movie lover",
  "favorite_genres": ["action", "sci-fi"]
}
```

### Change Password
`POST /auth/users/change_password/`
```json
{
  "old_password": "OldPass123",
  "new_password": "NewPass456",
  "new_password_confirm": "NewPass456"
}
```

### Token Refresh
`POST /auth/token/refresh/`

---

## Movie Endpoints

### Get Trending Movies (TMDb)
`GET /movies/movies/trending/?time_window=day&page=1`

### Search Movies (TMDb)
`GET /movies/movies/search/?q=avengers&page=1`

### Get Popular Movies (TMDb)
`GET /movies/movies/popular/?page=1`

### Get Top Rated Movies (TMDb)
`GET /movies/movies/top_rated/?page=1`

### Get Movie Details from TMDb
`GET /movies/movies/tmdb/{tmdb_id}/`

### List Movies (Database)
`GET /movies/movies/`

### Get Movie Details (Database)
`GET /movies/movies/{id}/`

### List Genres
`GET /movies/genres/`

### Sync Genres from TMDb
`POST /movies/genres/sync/`

---

## Favorites Endpoints (Requires Authentication)

### List User Favorites
`GET /favorites/favorites/`

### Add to Favorites
`POST /favorites/favorites/`
```json
{
  "movie": 1
}
```

### Remove from Favorites
`DELETE /favorites/favorites/{id}/`

### Check if Movie is Favorited
`GET /favorites/favorites/check/{movie_id}/`

---

## Ratings Endpoints (Requires Authentication)

### List User Ratings
`GET /favorites/ratings/`

### Rate a Movie
`POST /favorites/ratings/`
```json
{
  "movie": 1,
  "rating": 8.5
}
```

### Update Rating
`PATCH /favorites/ratings/{id}/`
```json
{
  "rating": 9.0
}
```

### Delete Rating
`DELETE /favorites/ratings/{id}/`

### Get Rating for Specific Movie
`GET /favorites/ratings/movie/{movie_id}/`

---

## Recommendations Endpoints (Requires Authentication)

### Get Recommendations
`GET /recommendations/`

### Refresh Recommendations
`POST /recommendations/refresh/`

### Get Similar Movies
`GET /recommendations/similar/{movie_id}/`

---

## Quick Test Commands

### 1. Register a user
```bash
curl -X POST http://localhost:8000/api/v1/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"TestPass123","password_confirm":"TestPass123"}'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

### 3. Get trending movies (no auth)
```bash
curl http://localhost:8000/api/v1/movies/movies/trending/
```

### 4. Search movies (no auth)
```bash
curl "http://localhost:8000/api/v1/movies/movies/search/?q=batman"
```

### 5. Add to favorites (with auth)
```bash
curl -X POST http://localhost:8000/api/v1/favorites/favorites/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"movie":1}'
```

### 6. Get recommendations (with auth)
```bash
curl http://localhost:8000/api/v1/recommendations/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Swagger Documentation
```
http://localhost:8000/api/schema/swagger-ui/
```

## ReDoc Documentation
```
http://localhost:8000/api/schema/redoc/
```

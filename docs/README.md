# 📚 Documentation Index

Welcome to the ALX Movie Recommendation API documentation. This directory contains all technical documentation for the project.

## 📖 Quick Links

### Getting Started
- **[Main README](../README.md)** - Project overview, features, and quick start
- **[Getting Started Guide](../GETTING_STARTED.md)** - Detailed installation and setup
- **[Project Status](../PROJECT_STATUS.md)** - Complete project status and metrics

### API Documentation
- **[API Reference](API_REFERENCE.md)** - Complete endpoint reference with examples
- **[Interactive API Docs](http://localhost:8000/api/docs/)** - Swagger UI (when server is running)
- **[OpenAPI Schema](http://localhost:8000/api/schema/)** - Machine-readable API spec

### Deployment & Operations
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **Health Checks**:
  - http://localhost:8000/api/v1/health/ - General health
  - http://localhost:8000/api/v1/health/liveness/ - Liveness probe
  - http://localhost:8000/api/v1/health/readiness/ - Readiness probe

---

## 📂 Documentation Structure

```
docs/
├── README.md                  # This file
├── API_REFERENCE.md          # Complete API endpoint reference
├── DEPLOYMENT_GUIDE.md       # Production deployment guide
├── API_PHASE1.md            # Phase 1 authentication documentation
└── archive/                  # Old/historical documentation
    ├── README_OLD.md
    ├── GETTING_STARTED_OLD.md
    ├── API_QUICK_REFERENCE.md
    ├── PROJECT_ROADMAP.md
    ├── PROJECT_COMPLETION.md
    └── IMPLEMENTATION_SUMMARY.md
```

---

## 🎯 Documentation by Use Case

### I want to...

#### **Install and Run the Project**
1. Read [Getting Started Guide](../GETTING_STARTED.md)
2. Follow the 8-step installation process
3. Verify with health check: `curl http://localhost:8000/api/v1/health/`

#### **Understand the API**
1. Review [API Reference](API_REFERENCE.md) for endpoint details
2. Visit [Swagger UI](http://localhost:8000/api/docs/) for interactive testing
3. Check example requests in [Main README](../README.md)

#### **Deploy to Production**
1. Read [Deployment Guide](DEPLOYMENT_GUIDE.md)
2. Review production checklist in [Project Status](../PROJECT_STATUS.md)
3. Configure environment variables from `.env.example`

#### **Check Project Status**
1. Review [Project Status](../PROJECT_STATUS.md)
2. Check [Main README](../README.md) for feature list
3. Run tests: `python manage.py test`

#### **Integrate with Frontend**
1. Review [API Reference](API_REFERENCE.md) for endpoints
2. Check authentication flow examples
3. Use Swagger UI to test endpoints
4. Review CORS configuration in settings

---

## 🔑 Key Endpoints

### Authentication
```bash
# Register
POST /api/v1/auth/

# Login
POST /api/v1/auth/login/

# Get current user
GET /api/v1/auth/me/
```

### Movies
```bash
# List movies
GET /api/v1/movies/

# Search movies
GET /api/v1/movies/search/?q=inception

# Trending movies
GET /api/v1/movies/trending/
```

### Favorites & Ratings
```bash
# Add favorite
POST /api/v1/favorites/

# Rate movie
POST /api/v1/favorites/ratings/

# Get user ratings
GET /api/v1/favorites/ratings/
```

### Recommendations
```bash
# Get recommendations
GET /api/v1/recommendations/

# Get similar movies
GET /api/v1/recommendations/similar/{movie_id}/
```

---

## 🛠️ API Documentation Tools

### Swagger UI
Interactive API documentation with request/response examples:
```
http://localhost:8000/api/docs/
```

### ReDoc
Alternative API documentation interface:
```
http://localhost:8000/api/redoc/
```

### OpenAPI Schema
Machine-readable API specification:
```
# YAML format (default)
http://localhost:8000/api/schema/

# JSON format
http://localhost:8000/api/schema/?format=json
```

---

## 📊 API Statistics

- **Total Endpoints**: 45+
- **Authentication**: JWT (access + refresh tokens)
- **Response Format**: JSON
- **Pagination**: Enabled for list endpoints
- **Rate Limiting**: Not configured (add in production)
- **API Version**: v1

---

## 🔒 Authentication

All endpoints (except health checks and documentation) require JWT authentication:

```bash
# 1. Login to get tokens
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "SecurePass123!"}'

# Response:
{
  "access": "eyJ0eXAiOiJKV1...",
  "refresh": "eyJ0eXAiOiJKV1..."
}

# 2. Use access token in subsequent requests
curl http://localhost:8000/api/v1/movies/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1..."
```

**Token Lifetime**:
- Access token: 60 minutes
- Refresh token: 7 days

---

## 🧪 Testing the API

### Using cURL
See examples in [API Reference](API_REFERENCE.md)

### Using Swagger UI
1. Start the server: `python manage.py runserver`
2. Visit http://localhost:8000/api/docs/
3. Click "Authorize" and enter your token
4. Test endpoints interactively

### Using Python requests
```python
import requests

# Login
response = requests.post(
    'http://localhost:8000/api/v1/auth/login/',
    json={'username': 'john', 'password': 'SecurePass123!'}
)
tokens = response.json()

# Use token
headers = {'Authorization': f'Bearer {tokens["access"]}'}
movies = requests.get(
    'http://localhost:8000/api/v1/movies/',
    headers=headers
).json()
```

---

## 📝 Response Format

### Success Response
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/movies/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response
```json
{
  "detail": "Authentication credentials were not provided."
}
```

Or:
```json
{
  "field_name": ["Error message"]
}
```

---

## 🌐 CORS Configuration

The API supports CORS for frontend integration. Allowed origins are configured in `settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
]
```

Update `CORS_ALLOWED_ORIGINS` in production settings.

---

## 📞 Support

- **Documentation Issues**: Check the [archive](archive/) for older versions
- **API Issues**: Use Swagger UI to test endpoints
- **Installation Issues**: Review [Getting Started](../GETTING_STARTED.md)
- **Project Status**: Check [Project Status](../PROJECT_STATUS.md)

---

## 🔄 Documentation Updates

**Last Updated**: February 11, 2026
**API Version**: v1
**Django Version**: 5.2.7
**DRF Version**: 3.16.1

---

## 📚 Additional Resources

### External Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [TMDb API Docs](https://developer.themoviedb.org/docs)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)

### Project Documentation
- Source code documentation in docstrings
- API schema at `/api/schema/`
- Django admin at `/admin/`

---

**Built with ❤️ for ALX Software Engineering Program**

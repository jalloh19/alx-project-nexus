"""
API v1 URL Configuration
Routes all v1 API endpoints
"""
from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    # Authentication
    path('auth/', include('apps.users.urls')),
    
    # Movies
    path('movies/', include('apps.movies.urls')),
    
    # Favorites & Ratings
    path('favorites/', include('apps.favorites.urls')),
    
    # Recommendations (ML-based)
    path('recommendations/', include('apps.recommendations.urls')),
]

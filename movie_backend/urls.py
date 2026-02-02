"""
URL configuration for movie_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include('api.v1.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),

    # Health Check
    path('health/', include('apps.core.urls')),
]

# Admin site customization
admin.site.site_header = "Movie Recommendation System"
admin.site.site_title = "Movie Admin"
admin.site.index_title = "Dashboard"

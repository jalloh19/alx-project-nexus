"""Recommendations URL configuration."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'recommendations'

router = DefaultRouter()
router.register(r'', views.RecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('', include(router.urls)),
]

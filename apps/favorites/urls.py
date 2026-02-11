"""Favorites URL configuration."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'favorites'

router = DefaultRouter()
router.register(r'ratings', views.RatingViewSet, basename='rating')
router.register(r'', views.FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
]

"""User URL configuration."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profiles', views.UserProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]

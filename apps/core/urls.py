"""Core URL configuration."""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.health_check, name='health'),
    path('ready/', views.readiness_check, name='readiness'),
    path('live/', views.liveness_check, name='liveness'),
]

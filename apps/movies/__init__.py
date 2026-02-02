"""Movies app - Movie data management and TMDb integration."""
from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.movies'
    verbose_name = 'Movies'

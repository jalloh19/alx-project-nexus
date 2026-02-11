"""
Movie models - Movie, Genre, and related models.
"""
from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel

User = get_user_model()


class Genre(TimeStampedModel):
    """Movie genre model."""
    tmdb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'genres'
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'
        ordering = ['name']

    def __str__(self):
        return self.name


class Movie(TimeStampedModel):
    """Movie model with TMDb data."""

    # TMDb fields
    tmdb_id = models.IntegerField(unique=True, db_index=True)
    imdb_id = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=500)
    original_title = models.CharField(max_length=500, blank=True)
    overview = models.TextField(blank=True)
    tagline = models.CharField(max_length=500, blank=True)

    # Release information
    release_date = models.DateField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True, help_text="Runtime in minutes")

    # Ratings and popularity
    vote_average = models.FloatField(default=0.0)
    vote_count = models.IntegerField(default=0)
    popularity = models.FloatField(default=0.0)

    # Media
    poster_path = models.CharField(max_length=200, blank=True, null=True)
    backdrop_path = models.CharField(max_length=200, blank=True, null=True)

    # Classification
    genres = models.ManyToManyField(Genre, related_name='movies', blank=True)
    original_language = models.CharField(max_length=10, default='en')
    adult = models.BooleanField(default=False)

    # Status
    status = models.CharField(max_length=50, blank=True)  # Released, Post Production, etc.

    # Additional metadata
    budget = models.BigIntegerField(null=True, blank=True)
    revenue = models.BigIntegerField(null=True, blank=True)
    homepage = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'movies'
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'
        ordering = ['-popularity', '-release_date']
        indexes = [
            models.Index(fields=['tmdb_id']),
            models.Index(fields=['title']),
            models.Index(fields=['-popularity']),
            models.Index(fields=['-release_date']),
            models.Index(fields=['-vote_average']),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'N/A'})"

    @property
    def poster_url(self):
        """Get full poster URL."""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None

    @property
    def backdrop_url(self):
        """Get full backdrop URL."""
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/original{self.backdrop_path}"
        return None


class WatchHistory(TimeStampedModel):
    """Track user's watch history."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watched_by')
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watch_history'
        verbose_name = 'Watch History'
        verbose_name_plural = 'Watch Histories'
        indexes = [
            models.Index(fields=['user', '-watched_at']),
        ]

    def __str__(self):
        return f"{self.user.email} watched {self.movie.title}"

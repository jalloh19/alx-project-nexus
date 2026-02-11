"""
Favorites app models.
"""
from django.db import models
from apps.users.models import User
from apps.movies.models import Movie
from apps.core.models import TimeStampedModel


class Favorite(TimeStampedModel):
    """User's favorite movies."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        db_table = 'favorites'
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        unique_together = ['user', 'movie']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.movie.title}"


class Rating(TimeStampedModel):
    """User ratings for movies."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_ratings')
    rating = models.FloatField()  # 0.5 to 5.0
    review = models.TextField(blank=True)

    class Meta:
        db_table = 'ratings'
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        unique_together = ['user', 'movie']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['movie', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} rated {self.movie.title}: {self.rating}"

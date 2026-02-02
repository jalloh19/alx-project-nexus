from django.db import models
from apps.core.models import BaseModel
from apps.users.models import User
from apps.movies.models import Movie


class Recommendation(BaseModel):
    """Store movie recommendations for users."""

    RECOMMENDATION_TYPES = [
        ('collaborative', 'Collaborative Filtering'),
        ('content_based', 'Content-Based'),
        ('hybrid', 'Hybrid'),
        ('trending', 'Trending'),
        ('personalized', 'Personalized'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    recommendation_type = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_TYPES,
        default='personalized'
    )
    score = models.FloatField(
        help_text="Recommendation confidence score (0-1)"
    )
    reason = models.TextField(
        blank=True,
        help_text="Explanation for why this movie is recommended"
    )
    is_clicked = models.BooleanField(
        default=False,
        help_text="Whether user clicked on this recommendation"
    )
    is_rated = models.BooleanField(
        default=False,
        help_text="Whether user rated this recommended movie"
    )

    class Meta:
        ordering = ['-score', '-created_at']
        unique_together = [['user', 'movie', 'recommendation_type']]
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['user', 'recommendation_type']),
        ]

    def __str__(self):
        return f"{self.movie.title} → {self.user.email} ({self.recommendation_type})"


class RecommendationFeedback(BaseModel):
    """Track user feedback on recommendations."""

    FEEDBACK_TYPES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('not_interested', 'Not Interested'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recommendation_feedbacks'
    )
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPES
    )
    comment = models.TextField(
        blank=True,
        help_text="Optional user comment"
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = [['user', 'recommendation']]

    def __str__(self):
        return f"{self.user.email} - {self.feedback_type} - {self.recommendation.movie.title}"

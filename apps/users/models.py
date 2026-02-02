"""
User models - Custom User and UserProfile models.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import TimeStampedModel


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return self.email


class UserProfile(TimeStampedModel):
    """
    User profile with additional information and preferences.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.URLField(blank=True, null=True)
    favorite_genres = models.JSONField(default=list, blank=True)

    # Preferences for recommendations
    preferred_language = models.CharField(max_length=10, default='en')
    mature_content = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.email}'s profile"

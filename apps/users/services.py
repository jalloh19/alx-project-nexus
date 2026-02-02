"""User service layer."""
from typing import Optional
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserService:
    """Service class for user-related business logic."""

    @staticmethod
    def create_user_with_profile(email: str, username: str, password: str, **extra_fields) -> User:
        """Create a new user with associated profile."""
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields
        )
        UserProfile.objects.create(user=user)
        return user

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def update_user_preferences(user: User, preferences: dict) -> UserProfile:
        """Update user profile preferences."""
        profile = user.profile

        if 'favorite_genres' in preferences:
            profile.favorite_genres = preferences['favorite_genres']
        if 'preferred_language' in preferences:
            profile.preferred_language = preferences['preferred_language']
        if 'mature_content' in preferences:
            profile.mature_content = preferences['mature_content']

        profile.save()
        return profile

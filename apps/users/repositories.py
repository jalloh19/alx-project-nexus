"""User repository for data access."""
from typing import List, Optional
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import UserProfile

User = get_user_model()


class UserRepository:
    """Repository for User model data access."""

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            return User.objects.select_related('profile').get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """Get user by email."""
        try:
            return User.objects.select_related('profile').get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def search_users(query: str) -> List[User]:
        """Search users by username or email."""
        return User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).select_related('profile')[:20]

    @staticmethod
    def get_active_users(limit: int = 100) -> List[User]:
        """Get recently active users."""
        return User.objects.filter(
            is_active=True
        ).select_related('profile').order_by('-last_login')[:limit]

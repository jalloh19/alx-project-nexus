"""
Pytest configuration and fixtures for testing.
"""
import pytest
from rest_framework.test import APIRequestFactory


@pytest.fixture
def rf():
    """Request factory fixture."""
    return APIRequestFactory()


@pytest.fixture
def api_client():
    """API client fixture."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def create_user():
    """Factory fixture for creating users."""
    from apps.users.models import User

    def _create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!@#',
        **kwargs
    ):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
    return _create_user


@pytest.fixture
def create_user_with_profile():
    """Factory fixture for creating users with profiles."""
    from apps.users.models import User, UserProfile

    def _create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!@#',
        **kwargs
    ):
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
        UserProfile.objects.get_or_create(user=user)
        return user
    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user_with_profile):
    """Authenticated API client fixture."""
    user = create_user_with_profile()
    api_client.force_authenticate(user=user)
    api_client.user = user
    return api_client

"""
Tests for user profile endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.users.models import User, UserProfile


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile endpoints."""

    def setup_method(self):
        """Setup test client and authenticated user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:profile-my-profile')

    def test_get_my_profile(self):
        """Test retrieving current user's profile."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert 'bio' in response.data
        assert 'avatar' in response.data
        assert 'favorite_genres' in response.data
        assert 'preferred_language' in response.data

    def test_update_my_profile(self):
        """Test updating current user's profile."""
        data = {
            'bio': 'Updated bio',
            'favorite_genres': ['action', 'comedy'],
            'preferred_language': 'fr',
            'mature_content': True
        }
        response = self.client.patch(self.url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['bio'] == 'Updated bio'
        assert response.data['favorite_genres'] == ['action', 'comedy']
        assert response.data['preferred_language'] == 'fr'
        assert response.data['mature_content'] is True

        # Verify in database
        self.profile.refresh_from_db()
        assert self.profile.bio == 'Updated bio'

    def test_update_profile_invalid_favorite_genres(self):
        """Test updating profile with invalid favorite_genres."""
        data = {
            'favorite_genres': 'not-a-list'
        }
        response = self.client.patch(self.url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_profile_created_on_registration(self):
        """Test that profile is automatically created on user registration."""
        # Create new user
        register_url = reverse('users:user-list')
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#'
        }
        self.client.force_authenticate(user=None)
        response = self.client.post(register_url, register_data)

        assert response.status_code == status.HTTP_201_CREATED

        # Verify profile exists
        new_user = User.objects.get(email='newuser@example.com')
        assert UserProfile.objects.filter(user=new_user).exists()

    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_avatar_url(self):
        """Test updating profile avatar URL."""
        data = {
            'avatar': 'https://example.com/avatar.jpg'
        }
        response = self.client.patch(self.url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['avatar'] == 'https://example.com/avatar.jpg'


@pytest.mark.django_db
class TestCurrentUser:
    """Test current user endpoint."""

    def setup_method(self):
        """Setup test client and authenticated user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User'
        )
        UserProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:user-me')

    def test_get_current_user(self):
        """Test retrieving current user details."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'test@example.com'
        assert response.data['username'] == 'testuser'
        assert response.data['first_name'] == 'Test'
        assert response.data['last_name'] == 'User'
        assert 'profile' in response.data
        assert 'full_name' in response.data

    def test_get_current_user_full_name(self):
        """Test full_name field in current user response."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'Test User'

    def test_get_current_user_full_name_empty(self):
        """Test full_name field when first/last names are empty."""
        self.user.first_name = ''
        self.user.last_name = ''
        self.user.save()

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'testuser'

    def test_update_current_user(self):
        """Test updating current user details."""
        data = {
            'username': 'updateduser',
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'updateduser'
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'

        # Verify in database
        self.user.refresh_from_db()
        assert self.user.username == 'updateduser'

    def test_update_current_user_duplicate_username(self):
        """Test updating username to existing username."""
        # Create another user
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='TestPass123!@#'
        )

        data = {'username': 'existinguser'}
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_current_user_unauthenticated(self):
        """Test getting current user without authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_current_user_cannot_change_email(self):
        """Test that email cannot be changed through update endpoint."""
        data = {'email': 'newemail@example.com'}
        response = self.client.patch(self.url, data)

        # Email should remain unchanged
        self.user.refresh_from_db()
        assert self.user.email == 'test@example.com'

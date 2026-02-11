"""
Tests for authentication endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.users.models import User, UserProfile


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration endpoint."""

    def setup_method(self):
        """Setup test client."""
        self.client = APIClient()
        self.url = reverse('users:user-list')

    def test_register_user_success(self):
        """Test successful user registration."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['email'] == 'test@example.com'
        assert response.data['user']['username'] == 'testuser'

        # Verify user and profile created in database
        user = User.objects.get(email='test@example.com')
        assert user.username == 'testuser'
        assert UserProfile.objects.filter(user=user).exists()

    def test_register_user_password_mismatch(self):
        """Test registration with mismatched passwords."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'DifferentPass123!@#',
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in str(response.data)

    def test_register_user_weak_password(self):
        """Test registration with weak password."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123',
            'password_confirm': '123',
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_duplicate_email(self):
        """Test registration with existing email."""
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='TestPass123!@#'
        )

        data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in str(response.data)

    def test_register_user_duplicate_username(self):
        """Test registration with existing username."""
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='TestPass123!@#'
        )

        data = {
            'username': 'testuser',
            'email': 'new@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in str(response.data)

    def test_register_user_short_username(self):
        """Test registration with username less than 3 characters."""
        data = {
            'username': 'ab',
            'email': 'test@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in str(response.data)

    def test_register_user_missing_required_fields(self):
        """Test registration with missing required fields."""
        data = {
            'username': 'testuser',
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Test user login endpoint."""

    def setup_method(self):
        """Setup test client and user."""
        self.client = APIClient()
        self.url = reverse('users:user-login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )

    def test_login_success(self):
        """Test successful login."""
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!@#'
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert 'user' in response.data

    def test_login_case_insensitive_email(self):
        """Test login with case-insensitive email."""
        data = {
            'email': 'TEST@EXAMPLE.COM',
            'password': 'TestPass123!@#'
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_200_OK

    def test_login_invalid_password(self):
        """Test login with invalid password."""
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_invalid_email(self):
        """Test login with invalid email."""
        data = {
            'email': 'wrong@example.com',
            'password': 'TestPass123!@#'
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_inactive_user(self):
        """Test login with inactive user."""
        self.user.is_active = False
        self.user.save()

        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!@#'
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_missing_fields(self):
        """Test login with missing fields."""
        data = {'email': 'test@example.com'}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogout:
    """Test user logout endpoint."""

    def setup_method(self):
        """Setup test client and authenticated user."""
        self.client = APIClient()
        self.url = reverse('users:user-logout')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )
        self.client.force_authenticate(user=self.user)

    def test_logout_success(self):
        """Test successful logout."""
        # First login to get tokens
        login_url = reverse('users:user-login')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!@#'
        }
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.data['tokens']['refresh']

        # Now logout
        logout_data = {'refresh': refresh_token}
        response = self.client.post(self.url, logout_data)

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data

    def test_logout_missing_token(self):
        """Test logout without refresh token."""
        response = self.client.post(self.url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_unauthenticated(self):
        """Test logout without authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {'refresh': 'some-token'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefresh:
    """Test token refresh endpoint."""

    def setup_method(self):
        """Setup test client and user."""
        self.client = APIClient()
        self.url = reverse('users:token_refresh')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )

    def test_token_refresh_success(self):
        """Test successful token refresh."""
        # First login to get tokens
        login_url = reverse('users:user-login')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!@#'
        }
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.data['tokens']['refresh']

        # Refresh the token
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(self.url, refresh_data)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token."""
        refresh_data = {'refresh': 'invalid-token'}
        response = self.client.post(self.url, refresh_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestChangePassword:
    """Test password change endpoint."""

    def setup_method(self):
        """Setup test client and authenticated user."""
        self.client = APIClient()
        self.url = reverse('users:user-change-password')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='OldPass123!@#'
        )
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        """Test successful password change."""
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#'
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_200_OK

        # Verify new password works
        self.user.refresh_from_db()
        assert self.user.check_password('NewPass123!@#')

    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password."""
        data = {
            'old_password': 'WrongPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#'
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_mismatch(self):
        """Test password change with mismatched new passwords."""
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'DifferentPass123!@#'
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_weak_new_password(self):
        """Test password change with weak new password."""
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': '123',
            'new_password_confirm': '123'
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_unauthenticated(self):
        """Test password change without authentication."""
        self.client.force_authenticate(user=None)
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#'
        }
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

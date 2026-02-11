"""
Tests for user serializers.
"""
import pytest
from django.contrib.auth import get_user_model
from apps.users.serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    LoginSerializer
)
from apps.users.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
class TestUserSerializer:
    """Test UserSerializer."""

    def test_user_serializer_fields(self):
        """Test UserSerializer contains expected fields."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User'
        )
        UserProfile.objects.create(user=user)

        serializer = UserSerializer(user)

        assert 'id' in serializer.data
        assert 'username' in serializer.data
        assert 'email' in serializer.data
        assert 'first_name' in serializer.data
        assert 'last_name' in serializer.data
        assert 'full_name' in serializer.data
        assert 'is_verified' in serializer.data
        assert 'date_joined' in serializer.data
        assert 'profile' in serializer.data
        assert 'password' not in serializer.data

    def test_user_serializer_full_name(self):
        """Test full_name method field."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User'
        )

        serializer = UserSerializer(user)
        assert serializer.data['full_name'] == 'Test User'


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    """Test UserRegistrationSerializer."""

    def test_registration_serializer_valid_data(self):
        """Test registration serializer with valid data."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)

        assert serializer.is_valid()

    def test_registration_serializer_password_mismatch(self):
        """Test registration serializer with password mismatch."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'DifferentPass123!@#'
        }
        serializer = UserRegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert 'password_confirm' in serializer.errors or 'non_field_errors' in serializer.errors

    def test_registration_serializer_duplicate_email(self):
        """Test registration serializer with duplicate email."""
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='TestPass123!@#'
        )

        data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#'
        }
        serializer = UserRegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_registration_serializer_duplicate_username(self):
        """Test registration serializer with duplicate username."""
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='TestPass123!@#'
        )

        data = {
            'username': 'testuser',
            'email': 'new@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#'
        }
        serializer = UserRegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_registration_serializer_short_username(self):
        """Test registration serializer with short username."""
        data = {
            'username': 'ab',
            'email': 'test@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#'
        }
        serializer = UserRegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_registration_serializer_create_user(self):
        """Test creating user through serializer."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#'
        }
        serializer = UserRegistrationSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.save()

        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('TestPass123!@#')
        assert UserProfile.objects.filter(user=user).exists()

    def test_registration_serializer_email_lowercase(self):
        """Test email is converted to lowercase."""
        data = {
            'username': 'testuser',
            'email': 'TEST@EXAMPLE.COM',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#'
        }
        serializer = UserRegistrationSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == 'test@example.com'


@pytest.mark.django_db
class TestUserUpdateSerializer:
    """Test UserUpdateSerializer."""

    def test_update_serializer_valid_data(self, rf):
        """Test update serializer with valid data."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )

        request = rf.patch('/')
        request.user = user

        data = {
            'username': 'updateduser',
            'first_name': 'Updated',
            'last_name': 'User'
        }
        serializer = UserUpdateSerializer(
            user,
            data=data,
            partial=True,
            context={'request': request}
        )

        assert serializer.is_valid()

    def test_update_serializer_duplicate_username(self, rf):
        """Test update serializer with duplicate username."""
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='TestPass123!@#'
        )
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='TestPass123!@#'
        )

        request = rf.patch('/')
        request.user = user1

        data = {'username': 'user2'}
        serializer = UserUpdateSerializer(
            user1,
            data=data,
            partial=True,
            context={'request': request}
        )

        assert not serializer.is_valid()
        assert 'username' in serializer.errors


@pytest.mark.django_db
class TestChangePasswordSerializer:
    """Test ChangePasswordSerializer."""

    def test_change_password_serializer_valid(self):
        """Test change password serializer with valid data."""
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#'
        }
        serializer = ChangePasswordSerializer(data=data)

        assert serializer.is_valid()

    def test_change_password_serializer_mismatch(self):
        """Test change password serializer with password mismatch."""
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'DifferentPass123!@#'
        }
        serializer = ChangePasswordSerializer(data=data)

        assert not serializer.is_valid()


@pytest.mark.django_db
class TestLoginSerializer:
    """Test LoginSerializer."""

    def test_login_serializer_valid_credentials(self, rf):
        """Test login serializer with valid credentials."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )

        request = rf.post('/')
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!@#'
        }
        serializer = LoginSerializer(data=data, context={'request': request})

        assert serializer.is_valid()
        assert serializer.validated_data['user'] == user

    def test_login_serializer_invalid_credentials(self, rf):
        """Test login serializer with invalid credentials."""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )

        request = rf.post('/')
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        serializer = LoginSerializer(data=data, context={'request': request})

        assert not serializer.is_valid()

    def test_login_serializer_inactive_user(self, rf):
        """Test login serializer with inactive user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )
        user.is_active = False
        user.save()

        request = rf.post('/')
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!@#'
        }
        serializer = LoginSerializer(data=data, context={'request': request})

        assert not serializer.is_valid()


@pytest.mark.django_db
class TestUserProfileSerializer:
    """Test UserProfileSerializer."""

    def test_profile_serializer_fields(self):
        """Test UserProfileSerializer contains expected fields."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )
        profile = UserProfile.objects.create(
            user=user,
            bio='Test bio',
            favorite_genres=['action', 'comedy']
        )

        serializer = UserProfileSerializer(profile)

        assert 'bio' in serializer.data
        assert 'avatar' in serializer.data
        assert 'favorite_genres' in serializer.data
        assert 'preferred_language' in serializer.data
        assert 'mature_content' in serializer.data
        assert 'created_at' in serializer.data
        assert 'updated_at' in serializer.data

    def test_profile_serializer_invalid_favorite_genres(self):
        """Test profile serializer with invalid favorite_genres."""
        data = {
            'favorite_genres': 'not-a-list'
        }
        serializer = UserProfileSerializer(data=data, partial=True)

        assert not serializer.is_valid()
        assert 'favorite_genres' in serializer.errors

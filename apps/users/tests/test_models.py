"""
Tests for user models.
"""
import pytest
from django.db import IntegrityError
from apps.users.models import User, UserProfile


@pytest.mark.django_db
class TestUserModel:
    """Test User model."""

    def test_create_user(self):
        """Test creating a user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )

        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('TestPass123!@#')
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!@#'
        )

        assert user.is_staff is True
        assert user.is_superuser is True

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )

        assert str(user) == 'test@example.com'

    def test_email_unique(self):
        """Test email uniqueness constraint."""
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='TestPass123!@#'
        )

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username='user2',
                email='test@example.com',
                password='TestPass123!@#'
            )

    def test_username_unique(self):
        """Test username uniqueness constraint."""
        User.objects.create_user(
            username='testuser',
            email='test1@example.com',
            password='TestPass123!@#'
        )

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username='testuser',
                email='test2@example.com',
                password='TestPass123!@#'
            )

    def test_user_username_field(self):
        """Test that email is the USERNAME_FIELD."""
        assert User.USERNAME_FIELD == 'email'

    def test_user_required_fields(self):
        """Test REQUIRED_FIELDS."""
        assert 'username' in User.REQUIRED_FIELDS


@pytest.mark.django_db
class TestUserProfileModel:
    """Test UserProfile model."""

    def test_create_user_profile(self):
        """Test creating a user profile."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )
        profile = UserProfile.objects.create(user=user)

        assert profile.user == user
        assert profile.bio == ''
        assert profile.avatar is None
        assert profile.favorite_genres == []
        assert profile.preferred_language == 'en'
        assert profile.mature_content is False

    def test_user_profile_str_representation(self):
        """Test user profile string representation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )
        profile = UserProfile.objects.create(user=user)

        assert str(profile) == "test@example.com's profile"

    def test_user_profile_one_to_one_relationship(self):
        """Test one-to-one relationship with user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )
        profile = UserProfile.objects.create(user=user)

        # Access profile from user
        assert user.profile == profile

    def test_user_profile_cascade_delete(self):
        """Test profile is deleted when user is deleted."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )
        profile = UserProfile.objects.create(user=user)
        profile_id = profile.id

        user.delete()

        assert not UserProfile.objects.filter(id=profile_id).exists()

    def test_user_profile_favorite_genres_json_field(self):
        """Test favorite_genres JSON field."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )
        profile = UserProfile.objects.create(
            user=user,
            favorite_genres=['action', 'comedy', 'drama']
        )

        profile.refresh_from_db()
        assert profile.favorite_genres == ['action', 'comedy', 'drama']
        assert isinstance(profile.favorite_genres, list)

    def test_user_profile_bio_max_length(self):
        """Test bio field max length."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )
        long_bio = 'a' * 600  # More than 500 characters

        with pytest.raises(Exception):  # DataError or ValidationError
            UserProfile.objects.create(
                user=user,
                bio=long_bio
            )

    def test_user_profile_timestamps(self):
        """Test created_at and updated_at timestamps."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!@#'
        )
        profile = UserProfile.objects.create(user=user)

        assert profile.created_at is not None
        assert profile.updated_at is not None
        assert profile.created_at == profile.updated_at

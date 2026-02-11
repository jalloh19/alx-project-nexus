"""User tests."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class UserModelTests(TestCase):
    """Tests for User model."""

    def test_create_user(self):
        """Test creating a new user."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_verified)


class UserAPITests(APITestCase):
    """Tests for User API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_user_registration(self):
        """Test user registration endpoint."""
        url = '/api/v1/auth/'
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123Strong!',
            'password_confirm': 'newpass123Strong!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

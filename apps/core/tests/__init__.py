"""Core tests."""
from django.test import TestCase, Client
from django.urls import reverse


class HealthCheckTests(TestCase):
    """Tests for health check endpoints."""

    def setUp(self):
        self.client = Client()

    def test_health_check_endpoint(self):
        """Test health check returns 200."""
        response = self.client.get(reverse('core:health'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())

    def test_readiness_check_endpoint(self):
        """Test readiness check returns 200."""
        response = self.client.get(reverse('core:readiness'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ready')

    def test_liveness_check_endpoint(self):
        """Test liveness check returns 200."""
        response = self.client.get(reverse('core:liveness'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'alive')

"""Tests for POST /api/login/."""

# Third-party
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class LoginAPITest(APITestCase):
    """Test suite for login endpoint."""

    def setUp(self):
        """Create test user and client."""
        self.client = APIClient()
        self.url = '/api/login/'
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='TestPass123!'
        )

    def test_success_returns_200_with_token(self):
        """Test successful login returns 200 with token."""
        response = self.client.post(
            self.url, {'username': 'testuser', 'password': 'TestPass123!'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_wrong_password_returns_400(self):
        """Test incorrect password returns 400."""
        response = self.client.post(
            self.url, {'username': 'testuser', 'password': 'Wrong!'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_user_returns_400(self):
        """Test unknown username returns 400."""
        response = self.client.post(
            self.url, {'username': 'nobody', 'password': 'TestPass123!'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_body_returns_400(self):
        """Test empty request body returns 400."""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
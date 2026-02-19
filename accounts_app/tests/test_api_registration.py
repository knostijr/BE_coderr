"""Tests for registration API endpoint."""

# Third-party imports
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class RegistrationAPITest(APITestCase):
    """Test cases for POST /api/registration/."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = '/api/registration/'

    def test_success_returns_201_with_token(self):
        """Test successful registration returns 201 with token."""
        data = {
            'username': 'newuser', 'email': 'new@test.com',
            'password': 'TestPass123!', 'repeated_password': 'TestPass123!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)

    def test_business_type_saved(self):
        """Test business type registration saves correct type."""
        data = {
            'username': 'biz', 'email': 'biz@test.com',
            'password': 'TestPass123!', 'repeated_password': 'TestPass123!',
            'type': 'business'
        }
        self.client.post(self.url, data, format='json')
        self.assertEqual(User.objects.get(username='biz').type, 'business')

    def test_password_mismatch_returns_400(self):
        """Test mismatched passwords return 400."""
        data = {
            'username': 'user', 'email': 'u@test.com',
            'password': 'TestPass123!', 'repeated_password': 'Wrong!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_email_returns_400(self):
        """Test missing email returns 400."""
        data = {
            'username': 'user',
            'password': 'TestPass123!', 'repeated_password': 'TestPass123!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_username_returns_400(self):
        """Test duplicate username returns 400."""
        User.objects.create_user(
            username='existing', email='e@test.com', password='TestPass123!'
        )
        data = {
            'username': 'existing', 'email': 'new@test.com',
            'password': 'TestPass123!', 'repeated_password': 'TestPass123!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_saved_to_database(self):
        """Test token is persisted in database after registration."""
        data = {
            'username': 'tok', 'email': 'tok@test.com',
            'password': 'TestPass123!', 'repeated_password': 'TestPass123!'
        }
        self.client.post(self.url, data, format='json')
        user = User.objects.get(username='tok')
        self.assertTrue(Token.objects.filter(user=user).exists())
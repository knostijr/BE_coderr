"""Tests for accounts permission requirements."""

# Third-party
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class AccountsPermissionTest(APITestCase):
    """Test that all permissions are correctly enforced."""

    def setUp(self):
        """Create two test users."""
        self.client = APIClient()
        self.user_a = User.objects.create_user(
            username='usera', email='a@test.com', password='TestPass123!'
        )
        self.user_b = User.objects.create_user(
            username='userb', email='b@test.com', password='TestPass123!'
        )

    def test_registration_is_public(self):
        """Test registration needs no token."""
        data = {
            'username': 'new', 'email': 'new@test.com',
            'password': 'TestPass123!', 'repeated_password': 'TestPass123!'
        }
        response = self.client.post('/api/registration/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_is_public(self):
        """Test login needs no token."""
        response = self.client.post(
            '/api/login/', {'username': 'usera', 'password': 'TestPass123!'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_get_requires_auth(self):
        """Test GET profile returns 401 without token."""
        response = self.client.get(f'/api/profile/{self.user_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_patch_requires_auth(self):
        """Test PATCH profile returns 401 without token."""
        response = self.client.patch(
            f'/api/profile/{self.user_a.id}/', {'location': 'X'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_b_cannot_patch_user_a(self):
        """Test user B cannot patch user A's profile."""
        self.client.force_authenticate(user=self.user_b)
        response = self.client.patch(
            f'/api/profile/{self.user_a.id}/', {'location': 'X'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
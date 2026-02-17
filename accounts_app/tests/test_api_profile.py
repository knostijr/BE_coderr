"""Tests for profile API endpoints."""

# Third-party
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class ProfileRetrieveAPITest(APITestCase):
    """Tests for GET /api/profile/{pk}/."""

    def setUp(self):
        """Create and authenticate test user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile_returns_200(self):
        """Test retrieving profile returns 200."""
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_has_user_field_not_id(self):
        """Test response has 'user' field, not 'id'."""
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertIn('user', response.data)
        self.assertNotIn('id', response.data)

    def test_string_fields_never_null(self):
        """Test profile string fields return empty string not null."""
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertEqual(response.data['location'], '')
        self.assertEqual(response.data['tel'], '')
        self.assertEqual(response.data['description'], '')
        self.assertEqual(response.data['working_hours'], '')

    def test_unauthenticated_returns_401(self):
        """Test unauthenticated request returns 401."""
        self.client.force_authenticate(user=None)
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_found_returns_404(self):
        """Test non-existent profile ID returns 404."""
        response = self.client.get('/api/profile/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProfileUpdateAPITest(APITestCase):
    """Tests for PATCH /api/profile/{pk}/."""

    def setUp(self):
        """Create two users for owner/non-owner tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='owner', email='owner@test.com', password='TestPass123!'
        )
        self.other = User.objects.create_user(
            username='other', email='other@test.com', password='TestPass123!'
        )

    def test_owner_can_update_profile(self):
        """Test owner can successfully update their profile."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f'/api/profile/{self.user.id}/', {'location': 'Berlin'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Berlin')

    def test_non_owner_gets_403(self):
        """Test non-owner gets 403 when updating another's profile."""
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            f'/api/profile/{self.user.id}/', {'location': 'Munich'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_gets_401(self):
        """Test unauthenticated PATCH returns 401."""
        response = self.client.patch(
            f'/api/profile/{self.user.id}/', {'location': 'Berlin'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileListAPITest(APITestCase):
    """Tests for GET /api/profiles/business/ and /api/profiles/customer/."""

    def setUp(self):
        """Create one business and one customer user."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='cust@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.client.force_authenticate(user=self.customer)

    def test_business_list_only_returns_business_users(self):
        """Test business endpoint only returns business type users."""
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(u['type'] == 'business' for u in response.data))

    def test_customer_list_only_returns_customer_users(self):
        """Test customer endpoint only returns customer type users."""
        response = self.client.get('/api/profiles/customer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(u['type'] == 'customer' for u in response.data))

    def test_business_list_is_plain_array(self):
        """Test business list returns array not paginated object."""
        response = self.client.get('/api/profiles/business/')
        self.assertIsInstance(response.data, list)

    def test_customer_list_is_plain_array(self):
        """Test customer list returns array not paginated object."""
        response = self.client.get('/api/profiles/customer/')
        self.assertIsInstance(response.data, list)

    def test_unauthenticated_gets_401(self):
        """Test unauthenticated request returns 401."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
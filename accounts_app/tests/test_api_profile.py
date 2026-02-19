"""Tests for profile API endpoints."""

# Third-party imports
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class ProfileRetrieveAPITest(APITestCase):
    """Tests for GET /api/profile/{pk}/."""

    def setUp(self):
        """Set up users and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='TestPass123!'
        )

    def test_get_profile_returns_200(self):
        """Test retrieving profile returns 200."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_has_user_field_not_id(self):
        """Test response has 'user' field not 'id' per endpoint docs."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertIn('user', response.data)
        self.assertNotIn('id', response.data)

    def test_response_has_no_updated_at(self):
        """Test response does not contain updated_at per endpoint docs."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertNotIn('updated_at', response.data)

    def test_response_has_created_at(self):
        """Test response contains created_at."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertIn('created_at', response.data)

    def test_string_fields_never_null(self):
        """Test profile string fields return empty string not null."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertEqual(response.data['location'], '')
        self.assertEqual(response.data['tel'], '')
        self.assertEqual(response.data['description'], '')
        self.assertEqual(response.data['working_hours'], '')

    def test_unauthenticated_returns_401(self):
        """Test unauthenticated request returns 401."""
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_found_returns_404(self):
        """Test non-existent profile ID returns 404."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profile/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProfileUpdateAPITest(APITestCase):
    """Tests for PATCH /api/profile/{pk}/."""

    def setUp(self):
        """Set up users and client."""
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
            f'/api/profile/{self.user.id}/',
            {'location': 'Berlin'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Berlin')

    def test_non_owner_gets_403(self):
        """Test non-owner gets 403 when updating another profile."""
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            f'/api/profile/{self.user.id}/',
            {'location': 'Munich'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_gets_401(self):
        """Test unauthenticated PATCH returns 401."""
        response = self.client.patch(
            f'/api/profile/{self.user.id}/',
            {'location': 'Berlin'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileListAPITest(APITestCase):
    """Tests for business and customer profile list endpoints."""

    def setUp(self):
        """Set up users of different types."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='cust@test.com',
            password='TestPass123!', type='customer'
        )
        User.objects.create_user(
            username='biz', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.client.force_authenticate(user=self.customer)

    def test_business_list_is_plain_array(self):
        """Test business list returns array not paginated object."""
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_business_list_only_business_users(self):
        """Test business endpoint only returns business type users."""
        response = self.client.get('/api/profiles/business/')
        for profile in response.data:
            self.assertEqual(profile['type'], 'business')

    def test_customer_list_is_plain_array(self):
        """Test customer list returns array not paginated object."""
        response = self.client.get('/api/profiles/customer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_customer_list_only_customer_users(self):
        """Test customer endpoint only returns customer type users."""
        response = self.client.get('/api/profiles/customer/')
        for profile in response.data:
            self.assertEqual(profile['type'], 'customer')

    def test_unauthenticated_gets_401(self):
        """Test unauthenticated request returns 401."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AccountsPermissionTest(APITestCase):
    """Tests verifying correct permission enforcement."""

    def setUp(self):
        """Set up two users."""
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
            'username': 'newuser', 'email': 'new@test.com',
            'password': 'TestPass123!', 'repeated_password': 'TestPass123!'
        }
        response = self.client.post('/api/registration/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_is_public(self):
        """Test login needs no token."""
        response = self.client.post(
            '/api/login/',
            {'username': 'usera', 'password': 'TestPass123!'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_get_requires_auth(self):
        """Test GET profile returns 401 without token."""
        response = self.client.get(f'/api/profile/{self.user_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_patch_requires_auth(self):
        """Test PATCH profile returns 401 without token."""
        response = self.client.patch(
            f'/api/profile/{self.user_a.id}/',
            {'location': 'Berlin'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_b_cannot_patch_user_a(self):
        """Test user B cannot patch user A profile."""
        self.client.force_authenticate(user=self.user_b)
        response = self.client.patch(
            f'/api/profile/{self.user_a.id}/',
            {'location': 'Berlin'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
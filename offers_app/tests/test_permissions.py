"""Tests for offers permission requirements."""

# Third-party
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

# Local
from offers_app.models import Offer

User = get_user_model()


class OffersPermissionTest(APITestCase):
    """Test all permission rules for offers endpoints."""

    def setUp(self):
        """Create test users and offer."""
        self.client = APIClient()
        self.business = User.objects.create_user(
            username='biz', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.customer = User.objects.create_user(
            username='cust', email='cust@test.com',
            password='TestPass123!', type='customer'
        )
        self.offer = Offer.objects.create(
            user=self.business, title='Test', description='Test'
        )

    def test_list_offers_is_public(self):
        """Test offer list is public."""
        response = self.client.get('/api/offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_create_offer(self):
        """Test customer gets 403 when creating offer."""
        self.client.force_authenticate(user=self.customer)
        data = {'title': 'T', 'description': 'D', 'details': []}
        response = self.client.post('/api/offers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_owner_cannot_delete(self):
        """Test non-owner gets 403 on delete."""
        stranger = User.objects.create_user(
            username='str', email='str@test.com',
            password='TestPass123!', type='business'
        )
        self.client.force_authenticate(user=stranger)
        response = self.client.delete(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
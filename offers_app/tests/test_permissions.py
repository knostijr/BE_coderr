"""Tests for offers permission requirements."""

# Third-party imports
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

# Local imports
from offers_app.models import Offer, OfferDetail

User = get_user_model()

VALID_DETAILS = [
    {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 3,
     'price': 50, 'features': [], 'offer_type': 'basic'},
    {'title': 'Standard', 'revisions': 3, 'delivery_time_in_days': 5,
     'price': 100, 'features': [], 'offer_type': 'standard'},
    {'title': 'Premium', 'revisions': 5, 'delivery_time_in_days': 7,
     'price': 200, 'features': [], 'offer_type': 'premium'},
]


class OffersPermissionTest(APITestCase):
    """Tests verifying correct permission enforcement for offers."""

    def setUp(self):
        """Create users and offer."""
        self.client = APIClient()
        self.business = User.objects.create_user(
            username='business', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.customer = User.objects.create_user(
            username='customer', email='cust@test.com',
            password='TestPass123!', type='customer'
        )
        self.offer = Offer.objects.create(
            user=self.business, title='Test', description='Test'
        )
        for detail in VALID_DETAILS:
            OfferDetail.objects.create(offer=self.offer, **detail)

    def test_list_is_public(self):
        """GET /api/offers/ is accessible without auth."""
        response = self.client.get('/api/offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_requires_auth(self):
        """GET /api/offers/{id}/ returns 401 without token."""
        response = self.client.get(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_requires_business_type(self):
        """POST /api/offers/ returns 403 for customer users."""
        self.client.force_authenticate(user=self.customer)
        data = {'title': 'Offer', 'description': 'Desc', 'details': VALID_DETAILS}
        response = self.client.post('/api/offers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_requires_ownership(self):
        """PATCH /api/offers/{id}/ returns 403 for non-owner."""
        other = User.objects.create_user(
            username='other', email='other@test.com',
            password='TestPass123!', type='business'
        )
        self.client.force_authenticate(user=other)
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/', {'title': 'X'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offerdetail_requires_auth(self):
        """GET /api/offerdetails/{id}/ returns 401 without token."""
        detail = OfferDetail.objects.filter(offer=self.offer).first()
        response = self.client.get(f'/api/offerdetails/{detail.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
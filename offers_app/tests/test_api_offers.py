"""Tests for offers API endpoints."""

# Third-party
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

# Local
from offers_app.models import Offer, OfferDetail

User = get_user_model()

VALID_DETAILS = [
    {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 3,
     'price': '50.00', 'features': ['F1'], 'offer_type': 'basic'},
    {'title': 'Standard', 'revisions': 3, 'delivery_time_in_days': 5,
     'price': '100.00', 'features': ['F1', 'F2'], 'offer_type': 'standard'},
    {'title': 'Premium', 'revisions': 5, 'delivery_time_in_days': 7,
     'price': '200.00', 'features': ['F1', 'F2', 'F3'], 'offer_type': 'premium'},
]


class OfferListAPITest(APITestCase):
    """Tests for GET /api/offers/ and POST /api/offers/."""

    def setUp(self):
        """Create business user and client."""
        self.client = APIClient()
        self.business = User.objects.create_user(
            username='biz', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.customer = User.objects.create_user(
            username='cust', email='cust@test.com',
            password='TestPass123!', type='customer'
        )

    def test_list_offers_is_public(self):
        """Test offer list is accessible without auth."""
        response = self.client.get('/api/offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_offer_as_business_returns_201(self):
        """Test business user can create offer."""
        self.client.force_authenticate(user=self.business)
        data = {'title': 'Design', 'description': 'Desc', 'details': VALID_DETAILS}
        response = self.client.post('/api/offers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_offer_as_customer_returns_403(self):
        """Test customer cannot create offer (403)."""
        self.client.force_authenticate(user=self.customer)
        data = {'title': 'Design', 'description': 'Desc', 'details': VALID_DETAILS}
        response = self.client.post('/api/offers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_offer_unauthenticated_returns_401(self):
        """Test unauthenticated offer creation returns 401."""
        data = {'title': 'Design', 'description': 'Desc', 'details': VALID_DETAILS}
        response = self.client.post('/api/offers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_without_3_details_returns_400(self):
        """Test creating offer with fewer than 3 details returns 400."""
        self.client.force_authenticate(user=self.business)
        data = {'title': 'Design', 'description': 'Desc', 'details': [VALID_DETAILS[0]]}
        response = self.client.post('/api/offers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OfferDetailAPITest(APITestCase):
    """Tests for GET, PATCH, DELETE /api/offers/{id}/."""

    def setUp(self):
        """Create business user and test offer."""
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username='owner', email='owner@test.com',
            password='TestPass123!', type='business'
        )
        self.other = User.objects.create_user(
            username='other', email='other@test.com',
            password='TestPass123!', type='business'
        )
        self.offer = Offer.objects.create(
            user=self.owner, title='Test', description='Test'
        )
        for d in VALID_DETAILS:
            OfferDetail.objects.create(offer=self.offer, **{
                **d, 'price': float(d['price'])
            })

    def test_get_offer_requires_auth(self):
        """Test GET single offer requires authentication."""
        response = self.client.get(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offer_authenticated_returns_200(self):
        """Test authenticated GET returns 200."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_patch_offer(self):
        """Test offer owner can update offer."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/', {'title': 'Updated'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_patch_returns_403(self):
        """Test non-owner cannot update offer."""
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/', {'title': 'Hacked'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_offer(self):
        """Test owner can delete their offer."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
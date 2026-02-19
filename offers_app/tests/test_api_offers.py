"""Tests for offers API endpoints."""

# Third-party imports
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

# Local imports
from offers_app.models import Offer, OfferDetail

User = get_user_model()

VALID_DETAILS = [
    {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 3,
     'price': 50, 'features': ['F1'], 'offer_type': 'basic'},
    {'title': 'Standard', 'revisions': 3, 'delivery_time_in_days': 5,
     'price': 100, 'features': ['F1', 'F2'], 'offer_type': 'standard'},
    {'title': 'Premium', 'revisions': 5, 'delivery_time_in_days': 7,
     'price': 200, 'features': ['F1', 'F2', 'F3'], 'offer_type': 'premium'},
]


class OfferListAPITest(APITestCase):
    """Tests for GET /api/offers/."""

    def setUp(self):
        """Create business user and offer."""
        self.client = APIClient()
        self.business = User.objects.create_user(
            username='biz', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.offer = Offer.objects.create(
            user=self.business, title='Test Offer', description='Test'
        )
        for d in VALID_DETAILS:
            OfferDetail.objects.create(offer=self.offer, **d)

    def test_list_is_public(self):
        """Test offer list is accessible without authentication."""
        response = self.client.get('/api/offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_is_paginated(self):
        """Test list response has count and results."""
        response = self.client.get('/api/offers/')
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)

    def test_list_contains_min_price(self):
        """Test list response contains min_price."""
        response = self.client.get('/api/offers/')
        self.assertIn('min_price', response.data['results'][0])

    def test_list_contains_min_delivery_time(self):
        """Test list response contains min_delivery_time."""
        response = self.client.get('/api/offers/')
        self.assertIn('min_delivery_time', response.data['results'][0])

    def test_list_contains_user_details(self):
        """Test list response contains user_details object."""
        response = self.client.get('/api/offers/')
        self.assertIn('user_details', response.data['results'][0])

    def test_list_details_have_id_and_url(self):
        """Test list details contain id and url only."""
        response = self.client.get('/api/offers/')
        detail = response.data['results'][0]['details'][0]
        self.assertIn('id', detail)
        self.assertIn('url', detail)

    def test_filter_by_creator_id(self):
        """Test filtering by creator_id."""
        response = self.client.get(f'/api/offers/?creator_id={self.business.id}')
        self.assertEqual(response.data['count'], 1)

    def test_search_by_title(self):
        """Test searching by title."""
        response = self.client.get('/api/offers/?search=Test')
        self.assertEqual(response.data['count'], 1)


class OfferCreateAPITest(APITestCase):
    """Tests for POST /api/offers/."""

    def setUp(self):
        """Create business and customer users."""
        self.client = APIClient()
        self.business = User.objects.create_user(
            username='biz', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.customer = User.objects.create_user(
            username='cust', email='cust@test.com',
            password='TestPass123!', type='customer'
        )

    def test_business_can_create_offer(self):
        """Test business user can create an offer."""
        self.client.force_authenticate(user=self.business)
        response = self.client.post(
            '/api/offers/',
            {'title': 'New', 'description': 'Desc', 'details': VALID_DETAILS},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_response_has_full_details(self):
        """Test POST response contains full detail objects not just urls."""
        self.client.force_authenticate(user=self.business)
        response = self.client.post(
            '/api/offers/',
            {'title': 'New', 'description': 'Desc', 'details': VALID_DETAILS},
            format='json'
        )
        detail = response.data['details'][0]
        self.assertIn('title', detail)
        self.assertIn('price', detail)
        self.assertIn('offer_type', detail)

    def test_customer_cannot_create_offer(self):
        """Test customer gets 403 when creating offer."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            '/api/offers/',
            {'title': 'New', 'description': 'Desc', 'details': VALID_DETAILS},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        """Test unauthenticated request returns 401."""
        response = self.client.post(
            '/api/offers/',
            {'title': 'New', 'description': 'Desc', 'details': VALID_DETAILS},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_less_than_3_details_returns_400(self):
        """Test offer without exactly 3 details returns 400."""
        self.client.force_authenticate(user=self.business)
        response = self.client.post(
            '/api/offers/',
            {'title': 'New', 'description': 'Desc', 'details': [VALID_DETAILS[0]]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OfferRetrieveAPITest(APITestCase):
    """Tests for GET /api/offers/{id}/."""

    def setUp(self):
        """Create users and offer."""
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
        for d in VALID_DETAILS:
            OfferDetail.objects.create(offer=self.offer, **d)

    def test_authenticated_can_retrieve(self):
        """Test authenticated user can retrieve single offer."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        """Test unauthenticated request returns 401."""
        response = self.client.get(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_returns_404(self):
        """Test nonexistent offer returns 404."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/offers/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_details_have_id_and_url(self):
        """Test retrieve details contain id and url."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f'/api/offers/{self.offer.id}/')
        detail = response.data['details'][0]
        self.assertIn('id', detail)
        self.assertIn('url', detail)

    def test_retrieve_has_no_user_details(self):
        """Test single offer retrieve does not have user_details."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f'/api/offers/{self.offer.id}/')
        self.assertNotIn('user_details', response.data)


class OfferUpdateDeleteAPITest(APITestCase):
    """Tests for PATCH and DELETE /api/offers/{id}/."""

    def setUp(self):
        """Create users and offer."""
        self.client = APIClient()
        self.business = User.objects.create_user(
            username='biz', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.other = User.objects.create_user(
            username='other', email='other@test.com',
            password='TestPass123!', type='business'
        )
        self.offer = Offer.objects.create(
            user=self.business, title='Test', description='Test'
        )
        for d in VALID_DETAILS:
            OfferDetail.objects.create(offer=self.offer, **d)

    def test_owner_can_update(self):
        """Test offer owner can update their offer."""
        self.client.force_authenticate(user=self.business)
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {'title': 'Updated'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_gets_403_on_update(self):
        """Test non-owner gets 403 updating offer."""
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {'title': 'Hack'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete(self):
        """Test offer owner can delete their offer."""
        self.client.force_authenticate(user=self.business)
        response = self.client.delete(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_owner_gets_403_on_delete(self):
        """Test non-owner gets 403 deleting offer."""
        self.client.force_authenticate(user=self.other)
        response = self.client.delete(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OfferDetailViewAPITest(APITestCase):
    """Tests for GET /api/offerdetails/{id}/."""

    def setUp(self):
        """Create users and offer detail."""
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
        self.detail = OfferDetail.objects.create(
            offer=self.offer, title='Basic', revisions=1,
            delivery_time_in_days=3, price=50.00,
            features=['F1'], offer_type='basic'
        )

    def test_authenticated_can_retrieve(self):
        """Test authenticated user can retrieve offer detail."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f'/api/offerdetails/{self.detail.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        """Test unauthenticated request returns 401."""
        response = self.client.get(f'/api/offerdetails/{self.detail.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OffersPermissionTest(APITestCase):
    """Tests verifying permission enforcement for offers."""

    def setUp(self):
        """Create users and offer."""
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
        for d in VALID_DETAILS:
            OfferDetail.objects.create(offer=self.offer, **d)

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
        response = self.client.post(
            '/api/offers/',
            {'title': 'O', 'description': 'D', 'details': VALID_DETAILS},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_requires_ownership(self):
        """PATCH /api/offers/{id}/ returns 403 for non-owner."""
        other = User.objects.create_user(
            username='other', email='other@test.com',
            password='TestPass123!', type='business'
        )
        self.client.force_authenticate(user=other)
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {'title': 'X'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
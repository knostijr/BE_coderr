"""Tests for orders permission requirements."""

# Third-party imports
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

# Local imports
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order

User = get_user_model()


class OrdersPermissionTest(APITestCase):
    """Tests verifying correct permission enforcement for orders."""

    def setUp(self):
        """Create users, offer, detail and order."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='customer', email='customer@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='business', email='business@test.com',
            password='TestPass123!', type='business'
        )
        self.offer = Offer.objects.create(
            user=self.business, title='Test', description='Test'
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer, title='Basic', revisions=1,
            delivery_time_in_days=3, price=50.00,
            features=[], offer_type='basic'
        )
        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            offer_detail=self.detail
        )

    def test_list_requires_auth(self):
        """GET /api/orders/ returns 401 without token."""
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_requires_customer_type(self):
        """POST /api/orders/ returns 403 for business users."""
        self.client.force_authenticate(user=self.business)
        response = self.client.post(
            '/api/orders/',
            {'offer_detail_id': self.detail.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_requires_business_type(self):
        """PATCH /api/orders/{id}/ returns 403 for customer users."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            {'status': 'completed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_requires_admin(self):
        """DELETE /api/orders/{id}/ returns 403 for non-admin users."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(f'/api/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_order(self):
        """DELETE /api/orders/{id}/ succeeds for admin/staff users."""
        admin = User.objects.create_user(
            username='admin', email='admin@test.com',
            password='TestPass123!', is_staff=True
        )
        self.client.force_authenticate(user=admin)
        response = self.client.delete(f'/api/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
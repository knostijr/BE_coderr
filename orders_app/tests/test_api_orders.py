"""Tests for orders API endpoints."""

# Third-party imports
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

# Local imports
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order

User = get_user_model()


def make_detail(business):
    """Create offer and detail for tests."""
    offer = Offer.objects.create(user=business, title='T', description='T')
    return OfferDetail.objects.create(
        offer=offer, title='Basic', revisions=1,
        delivery_time_in_days=3, price=50, features=[], offer_type='basic'
    )


class OrderListAPITest(APITestCase):
    """Tests for GET /api/orders/."""

    def setUp(self):
        """Create users and order."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )
        self.detail = make_detail(self.business)
        self.order = Order.objects.create(
            customer_user=self.customer, business_user=self.business,
            offer_detail=self.detail
        )

    def test_customer_sees_own_orders(self):
        """Test customer can see their own orders."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_business_sees_own_orders(self):
        """Test business user can see orders assigned to them."""
        self.client.force_authenticate(user=self.business)
        response = self.client.get('/api/orders/')
        self.assertEqual(len(response.data), 1)

    def test_response_is_plain_array(self):
        """Test response is a direct array not paginated."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/orders/')
        self.assertIsInstance(response.data, list)

    def test_response_contains_title(self):
        """Test response includes title from offer detail."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/orders/')
        self.assertIn('title', response.data[0])

    def test_response_contains_offer_fields(self):
        """Test response includes all OfferDetail fields."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/orders/')
        for field in ['revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']:
            self.assertIn(field, response.data[0])

    def test_unauthenticated_returns_401(self):
        """Test unauthenticated request returns 401."""
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unrelated_user_sees_no_orders(self):
        """Test user with no orders sees empty list."""
        other = User.objects.create_user(
            username='other', email='o@test.com',
            password='TestPass123!', type='customer'
        )
        self.client.force_authenticate(user=other)
        response = self.client.get('/api/orders/')
        self.assertEqual(len(response.data), 0)


class OrderCreateAPITest(APITestCase):
    """Tests for POST /api/orders/."""

    def setUp(self):
        """Create users and offer detail."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )
        self.detail = make_detail(self.business)

    def test_customer_can_create_order(self):
        """Test customer successfully creates an order."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            '/api/orders/', {'offer_detail_id': self.detail.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_response_has_full_data(self):
        """Test create response returns full order data."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            '/api/orders/', {'offer_detail_id': self.detail.id}, format='json'
        )
        for field in ['id', 'status', 'title', 'customer_user', 'business_user']:
            self.assertIn(field, response.data)

    def test_business_cannot_create_order(self):
        """Test business user gets 403 when creating order."""
        self.client.force_authenticate(user=self.business)
        response = self.client.post(
            '/api/orders/', {'offer_detail_id': self.detail.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_detail_id_returns_400(self):
        """Test invalid offer_detail_id returns 400."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            '/api/orders/', {'offer_detail_id': 9999}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_returns_401(self):
        """Test unauthenticated request returns 401."""
        response = self.client.post(
            '/api/orders/', {'offer_detail_id': self.detail.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderUpdateAPITest(APITestCase):
    """Tests for PATCH /api/orders/{id}/."""

    def setUp(self):
        """Create users and order."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )
        self.detail = make_detail(self.business)
        self.order = Order.objects.create(
            customer_user=self.customer, business_user=self.business,
            offer_detail=self.detail
        )

    def test_business_can_update_status(self):
        """Test business user can update order status."""
        self.client.force_authenticate(user=self.business)
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            {'status': 'completed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_update_status(self):
        """Test customer gets 403 when updating order status."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            {'status': 'completed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_business_cannot_update(self):
        """Test another business user gets 403 updating this order."""
        other = User.objects.create_user(
            username='other', email='o@test.com',
            password='TestPass123!', type='business'
        )
        self.client.force_authenticate(user=other)
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            {'status': 'completed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrderCountAPITest(APITestCase):
    """Tests for order-count and completed-order-count endpoints."""

    def setUp(self):
        """Create users and orders with different statuses."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )
        detail = make_detail(self.business)
        Order.objects.create(
            customer_user=self.customer, business_user=self.business,
            offer_detail=detail, status='in_progress'
        )
        Order.objects.create(
            customer_user=self.customer, business_user=self.business,
            offer_detail=detail, status='completed'
        )
        self.client.force_authenticate(user=self.customer)

    def test_order_count_returns_in_progress(self):
        """Test order-count returns number of in_progress orders."""
        response = self.client.get(f'/api/order-count/{self.business.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_completed_order_count(self):
        """Test completed-order-count returns completed orders."""
        response = self.client.get(
            f'/api/completed-order-count/{self.business.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)

    def test_invalid_user_returns_404(self):
        """Test order-count with non-existent user returns 404."""
        response = self.client.get('/api/order-count/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        """Test unauthenticated request returns 401."""
        self.client.force_authenticate(user=None)
        response = self.client.get(
            f'/api/completed-order-count/{self.business.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrdersPermissionTest(APITestCase):
    """Tests verifying permission enforcement for orders."""

    def setUp(self):
        """Create users and order."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )
        self.detail = make_detail(self.business)
        self.order = Order.objects.create(
            customer_user=self.customer, business_user=self.business,
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
            '/api/orders/', {'offer_detail_id': self.detail.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_requires_business_type(self):
        """PATCH /api/orders/{id}/ returns 403 for customer users."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(
            f'/api/orders/{self.order.id}/', {'status': 'completed'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_requires_admin(self):
        """DELETE /api/orders/{id}/ returns 403 for non-admin."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(f'/api/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_order(self):
        """DELETE /api/orders/{id}/ succeeds for admin users."""
        admin = User.objects.create_user(
            username='admin', email='admin@test.com',
            password='TestPass123!', is_staff=True
        )
        self.client.force_authenticate(user=admin)
        response = self.client.delete(f'/api/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
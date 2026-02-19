"""Tests for Order model."""

# Third-party imports
from django.contrib.auth import get_user_model
from django.test import TestCase

# Local imports
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order

User = get_user_model()


def create_detail(business):
    """Create offer and detail helper."""
    offer = Offer.objects.create(user=business, title='T', description='T')
    return OfferDetail.objects.create(
        offer=offer, title='Basic', revisions=1,
        delivery_time_in_days=3, price=50, features=[], offer_type='basic'
    )


class OrderModelTest(TestCase):
    """Test cases for Order model."""

    def setUp(self):
        """Create users and order."""
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )
        self.detail = create_detail(self.business)
        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            offer_detail=self.detail
        )

    def test_order_creation(self):
        """Test order is created with correct fields."""
        self.assertEqual(self.order.customer_user, self.customer)
        self.assertEqual(self.order.business_user, self.business)

    def test_default_status_is_in_progress(self):
        """Test default status is in_progress."""
        self.assertEqual(self.order.status, 'in_progress')

    def test_status_can_be_completed(self):
        """Test status can be set to completed."""
        self.order.status = 'completed'
        self.order.save()
        self.assertEqual(Order.objects.get(id=self.order.id).status, 'completed')

    def test_status_can_be_cancelled(self):
        """Test status can be set to cancelled."""
        self.order.status = 'cancelled'
        self.order.save()
        self.assertEqual(Order.objects.get(id=self.order.id).status, 'cancelled')

    def test_created_at_auto_set(self):
        """Test created_at is automatically set."""
        self.assertIsNotNone(self.order.created_at)

    def test_str_representation(self):
        """Test __str__ returns order ID and status."""
        self.assertEqual(str(self.order), f"Order #{self.order.id} - in_progress")

    def test_cascade_delete_on_customer(self):
        """Test deleting customer also deletes their orders."""
        order_id = self.order.id
        self.customer.delete()
        self.assertFalse(Order.objects.filter(id=order_id).exists())

    def test_cascade_delete_on_offer_detail(self):
        """Test deleting offer detail also deletes orders."""
        order_id = self.order.id
        self.detail.delete()
        self.assertFalse(Order.objects.filter(id=order_id).exists())
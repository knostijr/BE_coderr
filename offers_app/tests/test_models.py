"""Tests for Offer and OfferDetail models."""

# Third-party imports
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

# Local imports
from offers_app.models import Offer, OfferDetail

User = get_user_model()


class OfferModelTest(TestCase):
    """Test cases for Offer model."""

    def setUp(self):
        """Create business user and offer."""
        self.business = User.objects.create_user(
            username='biz', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.offer = Offer.objects.create(
            user=self.business, title='Test Offer', description='Test'
        )

    def test_offer_creation(self):
        """Test offer is created with correct fields."""
        self.assertEqual(self.offer.title, 'Test Offer')
        self.assertEqual(self.offer.user, self.business)

    def test_offer_str_representation(self):
        """Test __str__ returns offer title."""
        self.assertEqual(str(self.offer), 'Test Offer')

    def test_offer_image_optional(self):
        """Test image field is optional."""
        self.assertFalse(self.offer.image)

    def test_offer_created_at_auto_set(self):
        """Test created_at is auto-set."""
        self.assertIsNotNone(self.offer.created_at)

    def test_cascade_delete_with_user(self):
        """Test deleting user also deletes their offers."""
        offer_id = self.offer.id
        self.business.delete()
        self.assertFalse(Offer.objects.filter(id=offer_id).exists())


class OfferDetailModelTest(TestCase):
    """Test cases for OfferDetail model."""

    def setUp(self):
        """Create business user, offer and detail."""
        self.business = User.objects.create_user(
            username='biz', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.offer = Offer.objects.create(
            user=self.business, title='Test', description='Test'
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer, title='Basic', revisions=2,
            delivery_time_in_days=5, price=100.00,
            features=['Logo'], offer_type='basic'
        )

    def test_detail_creation(self):
        """Test offer detail is created correctly."""
        self.assertEqual(self.detail.title, 'Basic')
        self.assertEqual(float(self.detail.price), 100.00)

    def test_detail_str_representation(self):
        """Test __str__ returns offer title and type."""
        self.assertEqual(str(self.detail), 'Test - basic')

    def test_unique_offer_type_per_offer(self):
        """Test unique_together prevents duplicate offer_type."""
        with self.assertRaises(IntegrityError):
            OfferDetail.objects.create(
                offer=self.offer, title='Another Basic', revisions=1,
                delivery_time_in_days=3, price=50.00,
                features=[], offer_type='basic'
            )

    def test_cascade_delete_with_offer(self):
        """Test deleting offer also deletes its details."""
        detail_id = self.detail.id
        self.offer.delete()
        self.assertFalse(OfferDetail.objects.filter(id=detail_id).exists())
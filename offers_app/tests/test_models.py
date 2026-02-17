"""Tests for Offer and OfferDetail models."""

# Third-party
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

# Local
from offers_app.models import Offer, OfferDetail

User = get_user_model()


class OfferModelTest(TestCase):
    """Test suite for Offer model."""

    def setUp(self):
        """Create user and offer for testing."""
        self.user = User.objects.create_user(
            username='biz', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.offer = Offer.objects.create(
            user=self.user, title='Test Offer', description='Test'
        )

    def test_offer_creation(self):
        """Test offer created with correct fields."""
        self.assertEqual(self.offer.title, 'Test Offer')
        self.assertEqual(self.offer.user, self.user)

    def test_str_returns_title(self):
        """Test __str__ returns offer title."""
        self.assertEqual(str(self.offer), 'Test Offer')

    def test_image_is_optional(self):
        """Test image field can be empty."""
        self.assertFalse(self.offer.image)

    def test_cascade_delete_with_user(self):
        """Test offer deleted when user is deleted."""
        offer_id = self.offer.id
        self.user.delete()
        self.assertFalse(Offer.objects.filter(id=offer_id).exists())


class OfferDetailModelTest(TestCase):
    """Test suite for OfferDetail model."""

    def setUp(self):
        """Create offer for testing."""
        self.user = User.objects.create_user(
            username='biz', email='biz@test.com', password='TestPass123!'
        )
        self.offer = Offer.objects.create(
            user=self.user, title='Test', description='Test'
        )

    def test_detail_creation(self):
        """Test offer detail created with correct fields."""
        detail = OfferDetail.objects.create(
            offer=self.offer, title='Basic', revisions=1,
            delivery_time_in_days=3, price=50.00,
            features=['Feature 1'], offer_type='basic'
        )
        self.assertEqual(detail.price, 50.00)
        self.assertEqual(detail.offer_type, 'basic')

    def test_str_representation(self):
        """Test __str__ returns offer title with type."""
        detail = OfferDetail.objects.create(
            offer=self.offer, title='Basic', revisions=1,
            delivery_time_in_days=3, price=50.00,
            features=[], offer_type='basic'
        )
        self.assertEqual(str(detail), 'Test - basic')

    def test_duplicate_type_raises_integrity_error(self):
        """Test duplicate offer_type per offer raises IntegrityError."""
        OfferDetail.objects.create(
            offer=self.offer, title='B1', revisions=1,
            delivery_time_in_days=3, price=50.00,
            features=[], offer_type='basic'
        )
        with self.assertRaises(IntegrityError):
            OfferDetail.objects.create(
                offer=self.offer, title='B2', revisions=2,
                delivery_time_in_days=5, price=60.00,
                features=[], offer_type='basic'
            )

    def test_cascade_delete_with_offer(self):
        """Test details deleted when offer is deleted."""
        detail = OfferDetail.objects.create(
            offer=self.offer, title='Basic', revisions=1,
            delivery_time_in_days=3, price=50.00,
            features=[], offer_type='basic'
        )
        detail_id = detail.id
        self.offer.delete()
        self.assertFalse(OfferDetail.objects.filter(id=detail_id).exists())
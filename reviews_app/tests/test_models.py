"""Tests for Review model."""

# Third-party imports
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

# Local imports
from reviews_app.models import Review

User = get_user_model()


class ReviewModelTest(TestCase):
    """Test cases for Review model."""

    def setUp(self):
        """Create customer and business users."""
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )

    def test_review_creation(self):
        """Test review is created with correct fields."""
        review = Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=5, description='Excellent!'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.reviewer, self.customer)

    def test_str_representation(self):
        """Test __str__ returns reviewer and business user names."""
        review = Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=4, description='Good'
        )
        expected = f"Review by {self.customer.username} for {self.business.username}"
        self.assertEqual(str(review), expected)

    def test_created_at_auto_set(self):
        """Test created_at is automatically set."""
        review = Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=3, description='OK'
        )
        self.assertIsNotNone(review.created_at)

    def test_unique_review_per_business_user(self):
        """Test one customer can only review one business user once."""
        Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=5, description='Great'
        )
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                business_user=self.business, reviewer=self.customer,
                rating=3, description='Changed'
            )

    def test_cascade_delete_on_reviewer(self):
        """Test deleting reviewer also deletes their reviews."""
        review = Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=5, description='Great'
        )
        review_id = review.id
        self.customer.delete()
        self.assertFalse(Review.objects.filter(id=review_id).exists())
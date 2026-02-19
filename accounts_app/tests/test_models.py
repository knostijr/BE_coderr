"""Tests for User model."""

# Third-party imports
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""

    def setUp(self):
        """Create base test user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass123!'
        )

    def test_user_creation(self):
        """Test user created with correct credentials."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('TestPass123!'))

    def test_default_type_is_customer(self):
        """Test default type is customer."""
        self.assertEqual(self.user.type, 'customer')

    def test_business_type_saved_correctly(self):
        """Test business type is saved correctly."""
        user = User.objects.create_user(
            username='biz', email='biz@test.com',
            password='TestPass123!', type='business'
        )
        self.assertEqual(user.type, 'business')

    def test_string_fields_default_to_empty_string(self):
        """Test string fields default to empty string not null."""
        self.assertEqual(self.user.location, '')
        self.assertEqual(self.user.tel, '')
        self.assertEqual(self.user.description, '')
        self.assertEqual(self.user.working_hours, '')

    def test_created_at_auto_set(self):
        """Test created_at is auto-set on creation."""
        self.assertIsNotNone(self.user.created_at)

    def test_str_returns_username(self):
        """Test __str__ returns username."""
        self.assertEqual(str(self.user), 'testuser')

    def test_multiple_users_can_coexist(self):
        """Test multiple users can be created."""
        User.objects.create_user(
            username='user2', email='user2@test.com', password='TestPass123!'
        )
        self.assertEqual(User.objects.count(), 2)
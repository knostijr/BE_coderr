"""Tests for reviews API endpoints."""

# Third-party imports
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

# Local imports
from reviews_app.models import Review

User = get_user_model()


class ReviewListAPITest(APITestCase):
    """Tests for GET /api/reviews/."""

    def setUp(self):
        """Create users and a review."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )
        self.review = Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=5, description='Great!'
        )

    def test_list_returns_200(self):
        """Test authenticated user can list reviews."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_is_plain_array(self):
        """Test response is a direct array not paginated."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/reviews/')
        self.assertIsInstance(response.data, list)

    def test_filter_by_business_user_id(self):
        """Test filtering by business_user_id query param."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(
            f'/api/reviews/?business_user_id={self.business.id}'
        )
        self.assertEqual(len(response.data), 1)

    def test_filter_by_reviewer_id(self):
        """Test filtering by reviewer_id query param."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(
            f'/api/reviews/?reviewer_id={self.customer.id}'
        )
        self.assertEqual(len(response.data), 1)

    def test_unauthenticated_returns_401(self):
        """Test unauthenticated request returns 401."""
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewCreateAPITest(APITestCase):
    """Tests for POST /api/reviews/."""

    def setUp(self):
        """Create customer and business users."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )

    def test_customer_can_create_review(self):
        """Test customer successfully creates a review."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/reviews/', {
            'business_user': self.business.id,
            'rating': 5, 'description': 'Excellent!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reviewer_auto_set(self):
        """Test reviewer field is set from request user."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/reviews/', {
            'business_user': self.business.id,
            'rating': 4, 'description': 'Good!'
        }, format='json')
        self.assertEqual(response.data['reviewer'], self.customer.id)

    def test_duplicate_review_returns_400(self):
        """Test creating second review for same business returns 400."""
        Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=5, description='First'
        )
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/reviews/', {
            'business_user': self.business.id,
            'rating': 3, 'description': 'Second'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_business_cannot_create_review(self):
        """Test business user gets 403 when creating review."""
        self.client.force_authenticate(user=self.business)
        response = self.client.post('/api/reviews/', {
            'business_user': self.business.id,
            'rating': 5, 'description': 'Self'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        """Test unauthenticated request returns 401."""
        response = self.client.post('/api/reviews/', {
            'business_user': self.business.id,
            'rating': 5, 'description': 'Review'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewUpdateDeleteAPITest(APITestCase):
    """Tests for PATCH and DELETE /api/reviews/{id}/."""

    def setUp(self):
        """Create users and a review."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )
        self.other = User.objects.create_user(
            username='other', email='o@test.com',
            password='TestPass123!', type='customer'
        )
        self.review = Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=4, description='Good'
        )

    def test_reviewer_can_update(self):
        """Test reviewer can update their own review."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            {'rating': 5, 'description': 'Even better!'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)

    def test_other_user_cannot_update(self):
        """Test other user gets 403 updating review."""
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/', {'rating': 1}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviewer_can_delete(self):
        """Test reviewer can delete their own review."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(f'/api/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete(self):
        """Test other user gets 403 deleting review."""
        self.client.force_authenticate(user=self.other)
        response = self.client.delete(f'/api/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nonexistent_returns_404(self):
        """Test nonexistent review returns 404."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete('/api/reviews/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BaseInfoAPITest(APITestCase):
    """Tests for GET /api/base-info/."""

    def setUp(self):
        """Create users and reviews."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )
        Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=4, description='Good'
        )

    def test_returns_200(self):
        """Test base-info returns 200."""
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_is_public(self):
        """Test base-info requires no authentication."""
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contains_all_fields(self):
        """Test response contains all required fields."""
        response = self.client.get('/api/base-info/')
        for f in ['review_count', 'average_rating', 'business_profile_count', 'offer_count']:
            self.assertIn(f, response.data)

    def test_review_count_correct(self):
        """Test review_count matches actual number."""
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.data['review_count'], 1)

    def test_average_rating_one_decimal(self):
        """Test average_rating is rounded to 1 decimal place."""
        response = self.client.get('/api/base-info/')
        avg = response.data['average_rating']
        if avg is not None:
            self.assertEqual(avg, round(avg, 1))

    def test_business_count_correct(self):
        """Test business_profile_count is correct."""
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.data['business_profile_count'], 1)


class ReviewsPermissionTest(APITestCase):
    """Tests verifying permission enforcement for reviews."""

    def setUp(self):
        """Create users and a review."""
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username='cust', email='c@test.com',
            password='TestPass123!', type='customer'
        )
        self.business = User.objects.create_user(
            username='biz', email='b@test.com',
            password='TestPass123!', type='business'
        )
        self.review = Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=5, description='Great!'
        )

    def test_list_requires_auth(self):
        """GET /api/reviews/ returns 401 without token."""
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_requires_customer_type(self):
        """POST /api/reviews/ returns 403 for business users."""
        self.client.force_authenticate(user=self.business)
        response = self.client.post('/api/reviews/', {
            'business_user': self.business.id,
            'rating': 5, 'description': 'Self'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_requires_reviewer(self):
        """PATCH /api/reviews/{id}/ returns 403 for non-reviewer."""
        other = User.objects.create_user(
            username='o2', email='o2@test.com',
            password='TestPass123!', type='customer'
        )
        self.client.force_authenticate(user=other)
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/', {'rating': 1}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_requires_reviewer(self):
        """DELETE /api/reviews/{id}/ returns 403 for non-reviewer."""
        other = User.objects.create_user(
            username='o3', email='o3@test.com',
            password='TestPass123!', type='customer'
        )
        self.client.force_authenticate(user=other)
        response = self.client.delete(f'/api/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_base_info_is_public(self):
        """GET /api/base-info/ requires no authentication."""
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
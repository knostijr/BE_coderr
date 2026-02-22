# Coderr Backend API

Freelancer platform backend built with Django REST Framework. Business users create service offers, customers place orders and leave reviews.

## Tech Stack

- Python 3.12
- Django 4.2.7
- Django REST Framework 3.14.0
- django-filter 23.3
- Token Authentication (NOT JWT)
- SQLite3

## Getting Started

### Prerequisites
- Python 3.12+

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd coderr_backend

# 2. Create virtual environment
py -3.12 -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.template .env
# Generate SECRET_KEY:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Paste result into .env as: SECRET_KEY=<generated-key>

# 5. Run migrations
python manage.py migrate

# 6. Optional: Create superuser
python manage.py createsuperuser

# 7. Start server
python manage.py runserver
```

API: http://localhost:8000/api/
Admin: http://localhost:8000/admin/

## Authentication

Token Authentication. Include in all authenticated requests:
```
Authorization: Token <your-token-here>
```

## API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/registration/ | None | Register user |
| POST | /api/login/ | None | Login, get token |

### Profiles
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/profile/{id}/ | Required | Get profile |
| PATCH | /api/profile/{id}/ | Owner | Update profile |
| GET | /api/profiles/business/ | Required | List business users |
| GET | /api/profiles/customer/ | Required | List customers |

### Offers
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/offers/ | None | List offers (filterable) |
| POST | /api/offers/ | Business | Create offer |
| GET | /api/offers/{id}/ | Required | Get offer |
| PATCH | /api/offers/{id}/ | Owner | Update offer |
| DELETE | /api/offers/{id}/ | Owner | Delete offer |
| GET | /api/offerdetails/{id}/ | Required | Get package details |

**Offer Filters:**
- `creator_id` - Filter by business user ID
- `min_price` - Minimum price
- `max_delivery_time` - Maximum delivery days
- `search` - Search in title/description
- `ordering` - Sort by fields

### Orders
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/orders/ | Required | List own orders |
| POST | /api/orders/ | Customer | Create order |
| PATCH | /api/orders/{id}/ | Business | Update status |
| DELETE | /api/orders/{id}/ | Admin | Delete order |
| GET | /api/order-count/{id}/ | Required | In-progress count |
| GET | /api/completed-order-count/{id}/ | Required | Completed count |

### Reviews
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/reviews/ | Required | List reviews (filterable) |
| POST | /api/reviews/ | Customer | Create review |
| PATCH | /api/reviews/{id}/ | Reviewer | Update review |
| DELETE | /api/reviews/{id}/ | Reviewer | Delete review |

**Review Filters:**
- `business_user_id` - Filter by business user
- `reviewer_id` - Filter by reviewer

### Statistics
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/base-info/ | None | Platform statistics |

## Running Tests

```bash
# All tests
python manage.py test --verbosity=2

# Per app
python manage.py test accounts_app --verbosity=2
python manage.py test offers_app --verbosity=2
python manage.py test orders_app --verbosity=2
python manage.py test reviews_app --verbosity=2
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| SECRET_KEY | Django secret key (required) |
| DEBUG | True or False |

## Important Notes

- Database (db.sqlite3) is excluded from version control
- Business users can only create offers
- Customers can only create orders and reviews
- Maximum one review per customer per business user
- Orders can only be deleted by admin/staff users

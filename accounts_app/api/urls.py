"""URL routing for accounts_app API."""

# Third-party
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Local
from .views import (
    LoginView,
    ProfileBusinessListView,
    ProfileCustomerListView,
    ProfileViewSet,
    RegistrationView,
)

app_name = 'accounts_app'

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('profiles/business/', ProfileBusinessListView.as_view(), name='profile-business'),
    path('profiles/customer/', ProfileCustomerListView.as_view(), name='profile-customer'),
    path('', include(router.urls)),
]
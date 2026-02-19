"""URL configuration for accounts app."""

# Third-party imports
from django.urls import path

# Local imports
from .views import (
    LoginView,
    ProfileBusinessListView,
    ProfileCustomerListView,
    ProfileViewSet,
    RegistrationView,
)

app_name = 'accounts_app'

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path(
        'profile/<int:pk>/',
        ProfileViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}),
        name='profile-detail'
    ),
    path('profiles/business/', ProfileBusinessListView.as_view(), name='profile-business'),
    path('profiles/customer/', ProfileCustomerListView.as_view(), name='profile-customer'),
]
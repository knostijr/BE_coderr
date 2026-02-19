"""URL routing for offers app."""

# Third-party imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Local imports
from .views import OfferDetailViewSet, OfferViewSet

app_name = 'offers_app'

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'offerdetails', OfferDetailViewSet, basename='offerdetail')

urlpatterns = [
    path('', include(router.urls)),
]
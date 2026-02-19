"""URL routing for reviews app."""

# Third-party imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Local imports
from .views import BaseInfoView, ReviewViewSet

app_name = 'reviews_app'

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]
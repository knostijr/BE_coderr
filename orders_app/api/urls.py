"""URL routing for orders app."""

# Third-party imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Local imports
from .views import CompletedOrderCountView, OrderCountView, OrderViewSet

app_name = 'orders_app'

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'order-count/<int:business_user_id>/',
        OrderCountView.as_view(),
        name='order-count'
    ),
    path(
        'completed-order-count/<int:business_user_id>/',
        CompletedOrderCountView.as_view(),
        name='completed-order-count'
    ),
]
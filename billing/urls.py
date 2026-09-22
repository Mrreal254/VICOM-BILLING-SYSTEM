from django.urls import path

from .lifecycle_api import SubscriptionLifecycleView
from .views import (
    CustomerDetailView,
    CustomerListCreateView,
    PackageListCreateView,
    SubscriptionListCreateView,
)

urlpatterns = [
    path("customers/", CustomerListCreateView.as_view(), name="customer-list-create"),
    path("customers/<uuid:customer_id>/", CustomerDetailView.as_view(), name="customer-detail"),
    path("packages/", PackageListCreateView.as_view(), name="package-list-create"),
    path("subscriptions/", SubscriptionListCreateView.as_view(), name="subscription-list-create"),
    path("subscriptions/<int:subscription_id>/lifecycle/", SubscriptionLifecycleView.as_view(), name="subscription-lifecycle"),
]

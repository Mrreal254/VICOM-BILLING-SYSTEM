from django.urls import path

from .invoice_api import PlatformInvoiceGenerateView, SubscriptionInvoiceGenerateView
from .lifecycle_api import SubscriptionLifecycleView
from .views import (
    CustomerDetailView,
    CustomerListCreateView,
    PackageListCreateView,
    SubscriptionListCreateView,
)

urlpatterns = [
    path("customers/", CustomerListCreateView.as_view(), name="customer-list-create"),
    path("customers/<int:customer_id>/", CustomerDetailView.as_view(), name="customer-detail"),
    path("packages/", PackageListCreateView.as_view(), name="package-list-create"),
    path("subscriptions/", SubscriptionListCreateView.as_view(), name="subscription-list-create"),
    path("subscriptions/<int:subscription_id>/lifecycle/", SubscriptionLifecycleView.as_view(), name="subscription-lifecycle"),
    path("invoices/platform/generate/", PlatformInvoiceGenerateView.as_view(), name="platform-invoice-generate"),
    path("subscriptions/<int:subscription_id>/invoice/", SubscriptionInvoiceGenerateView.as_view(), name="subscription-invoice-generate"),
]

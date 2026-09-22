from django.urls import path

from .dashboard_views import BillingDashboardView
from .dashboard_ui import billing_dashboard
from .invoice_api import PlatformInvoiceGenerateView, SubscriptionInvoiceGenerateView
from .lifecycle_api import SubscriptionLifecycleView
from .payment_api import InvoicePaymentView, PaymentSuccessView
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
    path("subscriptions/<int:subscription_id>/invoice/", SubscriptionInvoiceGenerateView.as_view(), name="subscription-invoice-generate"),
    path("invoices/platform/generate/", PlatformInvoiceGenerateView.as_view(), name="platform-invoice-generate"),
    path("invoices/<int:invoice_id>/payments/", InvoicePaymentView.as_view(), name="invoice-payment-create"),
    path("payments/<int:payment_id>/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("dashboard/", BillingDashboardView.as_view(), name="billing-dashboard"),
    path("dashboard/ui/", billing_dashboard, name="billing-dashboard-ui"),
]

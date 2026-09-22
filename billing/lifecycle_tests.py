from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from tenants.models import Tenant
from .invoice_models import Invoice
from .invoice_service import generate_subscription_invoice
from .models import Customer, Package, Subscription


class SubscriptionLifecycleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(name="Lifecycle ISP", slug="lifecycle-isp", email="life@example.com", phone_number="+254700000041")
        self.user = User.objects.create_user(email="admin@life.example", password="StrongPass123!", role=User.Role.ISP_ADMIN, tenant=self.tenant)
        customer = Customer.objects.create(tenant=self.tenant, customer_number="L-001", full_name="Lifecycle Customer", phone_number="+254711000041")
        package = Package.objects.create(tenant=self.tenant, name="Monthly", price="1500.00", duration_days=30)
        self.subscription = Subscription.objects.create(tenant=self.tenant, customer=customer, package=package)
        self.client.force_authenticate(self.user)

    def test_activate_sets_dates_and_active_status(self):
        self.subscription.activate()
        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.status, Subscription.Status.ACTIVE)
        self.assertIsNotNone(self.subscription.start_date)
        self.assertEqual(self.subscription.end_date - self.subscription.start_date, timedelta(days=30))

    def test_suspend_and_cancel(self):
        self.subscription.activate()
        response = self.client.patch(f"/api/billing/subscriptions/{self.subscription.id}/lifecycle/", {"action": "suspend"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], Subscription.Status.SUSPENDED)
        response = self.client.patch(f"/api/billing/subscriptions/{self.subscription.id}/lifecycle/", {"action": "cancel"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], Subscription.Status.CANCELLED)

    def test_due_subscription_can_expire(self):
        self.subscription.activate(start_date=timezone.now() - timedelta(days=31))
        self.subscription.refresh_from_db()
        self.assertTrue(self.subscription.mark_expired_if_due())
        self.assertEqual(self.subscription.status, Subscription.Status.EXPIRED)

    def test_lifecycle_is_tenant_scoped(self):
        other_tenant = Tenant.objects.create(name="Other Lifecycle", slug="other-lifecycle", email="otherlife@example.com", phone_number="+254700000042")
        other_user = User.objects.create_user(email="other@life.example", password="StrongPass123!", role=User.Role.ISP_ADMIN, tenant=other_tenant)
        self.client.force_authenticate(other_user)
        response = self.client.patch(f"/api/billing/subscriptions/{self.subscription.id}/lifecycle/", {"action": "activate"}, format="json")
        self.assertEqual(response.status_code, 404)


class InvoiceGenerationTests(TestCase):
    def setUp(self):
        tenant = Tenant.objects.create(name="Invoice ISP", slug="invoice-isp", email="invoice@example.com", phone_number="+254700000043")
        customer = Customer.objects.create(tenant=tenant, customer_number="I-001", full_name="Invoice Customer", phone_number="+254711000043")
        package = Package.objects.create(tenant=tenant, name="Pro", price="2500.00", duration_days=30)
        self.subscription = Subscription.objects.create(tenant=tenant, customer=customer, package=package)

    def test_invoice_is_generated_from_subscription_price(self):
        invoice = generate_subscription_invoice(self.subscription, tax=Decimal("400.00"), due_days=14)
        self.assertEqual(invoice.status, Invoice.Status.ISSUED)
        self.assertEqual(invoice.subtotal, Decimal("2500.00"))
        self.assertEqual(invoice.tax, Decimal("400.00"))
        self.assertEqual(invoice.total, Decimal("2900.00"))
        self.assertEqual(invoice.balance_due, Decimal("2900.00"))
        self.assertEqual((invoice.due_date - invoice.issue_date).days, 14)
        self.assertTrue(invoice.invoice_number.startswith("INV-"))

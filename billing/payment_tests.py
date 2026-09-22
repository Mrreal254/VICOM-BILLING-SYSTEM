from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from tenants.models import Tenant
from .invoice_models import Invoice
from .models import Customer
from .payment_models import PaymentTransaction


class PaymentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tenant_a = Tenant.objects.create(name="ISP A", slug="isp-a", email="a@example.com", phone_number="+254700000041")
        self.tenant_b = Tenant.objects.create(name="ISP B", slug="isp-b", email="b@example.com", phone_number="+254700000042")
        self.user_a = User.objects.create_user(email="pay-a@example.com", password="StrongPass123!", role=User.Role.ISP_ADMIN, tenant=self.tenant_a)
        self.user_b = User.objects.create_user(email="pay-b@example.com", password="StrongPass123!", role=User.Role.ISP_ADMIN, tenant=self.tenant_b)
        self.customer_a = Customer.objects.create(tenant=self.tenant_a, customer_number="A-PAY-001", full_name="Customer A", phone_number="+254711000041")
        self.customer_b = Customer.objects.create(tenant=self.tenant_b, customer_number="B-PAY-001", full_name="Customer B", phone_number="+254711000042")
        self.invoice_a = Invoice.objects.create(
            tenant=self.tenant_a, customer=self.customer_a, invoice_number="INV-A-001",
            issue_date=date.today(), due_date=date.today(), subtotal=Decimal("2900.00"), total=Decimal("2900.00"), status=Invoice.Status.ISSUED,
        )
        self.invoice_b = Invoice.objects.create(
            tenant=self.tenant_b, customer=self.customer_b, invoice_number="INV-B-001",
            issue_date=date.today(), due_date=date.today(), subtotal=Decimal("1500.00"), total=Decimal("1500.00"), status=Invoice.Status.ISSUED,
        )

    def test_payment_creation_is_tenant_scoped(self):
        self.client.force_authenticate(self.user_a)
        response = self.client.post(f"/api/billing/invoices/{self.invoice_a.id}/payments/", {"amount": "1000.00", "reference": "PAY-A-001"}, format="json")
        self.assertEqual(response.status_code, 201)
        payment = PaymentTransaction.objects.get(reference="PAY-A-001")
        self.assertEqual(payment.tenant_id, self.tenant_a.id)

    def test_cannot_pay_another_tenant_invoice(self):
        self.client.force_authenticate(self.user_a)
        response = self.client.post(f"/api/billing/invoices/{self.invoice_b.id}/payments/", {"amount": "100.00", "reference": "PAY-A-002"}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_payment_above_balance_is_rejected(self):
        self.client.force_authenticate(self.user_a)
        response = self.client.post(f"/api/billing/invoices/{self.invoice_a.id}/payments/", {"amount": "3000.00", "reference": "PAY-A-003"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_successful_payment_updates_invoice(self):
        self.client.force_authenticate(self.user_a)
        create = self.client.post(f"/api/billing/invoices/{self.invoice_a.id}/payments/", {"amount": "2900.00", "reference": "PAY-A-004"}, format="json")
        self.assertEqual(create.status_code, 201)
        payment_id = create.data["id"]
        success = self.client.post(f"/api/billing/payments/{payment_id}/success/", {}, format="json")
        self.assertEqual(success.status_code, 200)
        self.invoice_a.refresh_from_db()
        self.assertEqual(self.invoice_a.amount_paid, Decimal("2900.00"))
        self.assertEqual(self.invoice_a.status, Invoice.Status.PAID)

    def test_partial_payment_marks_invoice_partially_paid(self):
        self.client.force_authenticate(self.user_a)
        create = self.client.post(f"/api/billing/invoices/{self.invoice_a.id}/payments/", {"amount": "1000.00", "reference": "PAY-A-005"}, format="json")
        payment_id = create.data["id"]
        self.client.post(f"/api/billing/payments/{payment_id}/success/", {}, format="json")
        self.invoice_a.refresh_from_db()
        self.assertEqual(self.invoice_a.amount_paid, Decimal("1000.00"))
        self.assertEqual(self.invoice_a.status, Invoice.Status.PARTIALLY_PAID)

    def test_duplicate_reference_is_rejected(self):
        self.client.force_authenticate(self.user_a)
        PaymentTransaction.objects.create(tenant=self.tenant_a, invoice=self.invoice_a, reference="DUP-001", amount=Decimal("100.00"))
        response = self.client.post(f"/api/billing/invoices/{self.invoice_a.id}/payments/", {"amount": "100.00", "reference": "DUP-001"}, format="json")
        self.assertEqual(response.status_code, 400)

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from tenants.models import Tenant
from .models import Customer, Package


class BillingTenantIsolationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tenant_a = Tenant.objects.create(name="ISP A", slug="isp-a", email="a@example.com", phone_number="+254700000031")
        self.tenant_b = Tenant.objects.create(name="ISP B", slug="isp-b", email="b@example.com", phone_number="+254700000032")
        self.user_a = User.objects.create_user(email="admin-a@example.com", password="StrongPass123!", role=User.Role.ISP_ADMIN, tenant=self.tenant_a)
        self.user_b = User.objects.create_user(email="admin-b@example.com", password="StrongPass123!", role=User.Role.ISP_ADMIN, tenant=self.tenant_b)
        self.customer_a = Customer.objects.create(tenant=self.tenant_a, customer_number="A-001", full_name="Customer A", phone_number="+254711000001")
        self.customer_b = Customer.objects.create(tenant=self.tenant_b, customer_number="B-001", full_name="Customer B", phone_number="+254711000002")
        self.package_a = Package.objects.create(tenant=self.tenant_a, name="A Basic", price="100.00")
        self.package_b = Package.objects.create(tenant=self.tenant_b, name="B Basic", price="200.00")

    def test_customer_list_is_tenant_scoped(self):
        self.client.force_authenticate(self.user_a)
        response = self.client.get("/api/billing/customers/")
        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.data}
        self.assertIn(self.customer_a.id, ids)
        self.assertNotIn(self.customer_b.id, ids)

    def test_customer_detail_cannot_cross_tenant(self):
        self.client.force_authenticate(self.user_a)
        response = self.client.get(f"/api/billing/customers/{self.customer_b.id}/")
        self.assertEqual(response.status_code, 404)

    def test_customer_creation_assigns_current_tenant(self):
        self.client.force_authenticate(self.user_a)
        response = self.client.post("/api/billing/customers/", {"customer_number": "A-002", "full_name": "New Customer", "phone_number": "+254711000003"}, format="json")
        self.assertEqual(response.status_code, 201)
        created = Customer.objects.get(customer_number="A-002", tenant=self.tenant_a)
        self.assertEqual(created.tenant_id, self.tenant_a.id)

    def test_package_list_is_tenant_scoped(self):
        self.client.force_authenticate(self.user_a)
        response = self.client.get("/api/billing/packages/")
        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.data}
        self.assertIn(self.package_a.id, ids)
        self.assertNotIn(self.package_b.id, ids)

    def test_cross_tenant_subscription_is_rejected(self):
        self.client.force_authenticate(self.user_a)
        response = self.client.post("/api/billing/subscriptions/", {"customer": self.customer_a.id, "package": self.package_b.id}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_billing_access_is_rejected(self):
        response = self.client.get("/api/billing/customers/")
        self.assertEqual(response.status_code, 401)

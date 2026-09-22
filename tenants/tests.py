from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from .models import Tenant


class TenantModelTests(TestCase):
    def test_tenant_defaults_to_pending(self):
        tenant = Tenant.objects.create(
            name="Test ISP",
            slug="test-isp",
            email="isp@example.com",
            phone_number="+254700000000",
        )
        self.assertEqual(tenant.status, Tenant.Status.PENDING)
        self.assertEqual(tenant.currency, "KES")
        self.assertEqual(tenant.timezone, "Africa/Nairobi")


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(
            name="Tenant One",
            slug="tenant-one",
            email="one@example.com",
            phone_number="+254700000001",
        )
        self.user = User.objects.create_user(
            email="admin@one.example",
            password="StrongPass123!",
            role=User.Role.ISP_ADMIN,
            tenant=self.tenant,
        )

    def test_authenticated_user_sees_only_own_tenant_context(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/tenants/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["tenant"]["id"], str(self.tenant.id))

    def test_user_without_tenant_is_forbidden(self):
        user = User.objects.create_user(
            email="staff@example.com",
            password="StrongPass123!",
            role=User.Role.ISP_STAFF,
        )
        self.client.force_authenticate(user)
        response = self.client.get("/api/tenants/dashboard/")
        self.assertEqual(response.status_code, 403)

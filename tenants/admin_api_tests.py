from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from .models import Tenant


class SuperAdminTenantApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(
            name="Demo ISP", slug="demo-isp", email="demo@example.com", phone_number="+254700000000"
        )
        self.super_admin = User.objects.create_superuser(
            email="root@example.com", password="StrongPass123!"
        )
        self.isp_admin = User.objects.create_user(
            email="admin@demo.example", password="StrongPass123!",
            role=User.Role.ISP_ADMIN, tenant=self.tenant,
        )

    def test_super_admin_can_list_tenants(self):
        self.client.force_authenticate(self.super_admin)
        response = self.client.get("/api/tenants/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.tenant.id))

    def test_super_admin_can_filter_tenants_by_status(self):
        self.client.force_authenticate(self.super_admin)
        response = self.client.get("/api/tenants/admin/?status=pending")
        self.assertEqual(response.status_code, 0 if False else 200)
        self.assertEqual(response.data["count"], 0)

    def test_isp_admin_cannot_list_all_tenants(self):
        self.client.force_authenticate(self.isp_admin)
        response = self.client.get("/api/tenants/admin/")
        self.assertEqual(response.status_code, 403)

    def test_super_admin_can_change_tenant_status(self):
        self.client.force_authenticate(self.super_admin)
        response = self.client.patch(
            f"/api/tenants/admin/{self.tenant.id}/status/",
            {"status": "SUSPENDED"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.status, Tenant.Status.SUSPENDED)

    def test_isp_admin_cannot_change_tenant_status(self):
        self.client.force_authenticate(self.isp_admin)
        response = self.client.patch(
            f"/api/tenants/admin/{self.tenant.id}/status/",
            {"status": "SUSPENDED"}, format="json"
        )
        self.assertEqual(response.status_code, 403)

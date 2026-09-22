from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from .models import Tenant


class DashboardApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(
            name="Dashboard ISP",
            slug="dashboard-isp",
            email="dashboard@example.com",
            phone_number="+254700000010",
        )
        self.isp_admin = User.objects.create_user(
            email="admin@dashboard.example",
            password="StrongPass123!",
            role=User.Role.ISP_ADMIN,
            tenant=self.tenant,
            first_name="ISP",
            last_name="Admin",
        )
        self.super_admin = User.objects.create_superuser(
            email="super@example.com",
            password="StrongPass123!",
        )

    def test_super_admin_dashboard_is_restricted(self):
        self.client.force_authenticate(self.isp_admin)
        response = self.client.get("/api/tenants/dashboard/super-admin/")
        self.assertEqual(response.status_code, 403)

    def test_isp_admin_dashboard_returns_only_own_tenant(self):
        other = Tenant.objects.create(
            name="Other ISP",
            slug="other-isp",
            email="other@example.com",
            phone_number="+254700000011",
        )
        self.client.force_authenticate(self.isp_admin)
        response = self.client.get("/api/tenants/dashboard/isp-admin/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["tenant"]["id"], str(self.tenant.id))
        self.assertNotEqual(response.data["tenant"]["id"], str(other.id))

    def test_super_admin_dashboard_returns_tenant_counts(self):
        self.client.force_authenticate(self.super_admin)
        response = self.client.get("/api/tenants/dashboard/super-admin/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["tenants"]["total"], 1)
        self.assertEqual(response.data["tenants"]["pending"], 1)

from django.test import TestCase
from rest_framework.test import APIClient

from .models import User
from tenants.models import Tenant


class UserModelTests(TestCase):
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            email="admin@example.com",
            password="StrongPass123!",
            role=User.Role.ISP_ADMIN,
        )
        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertEqual(user.username, None)

    def test_create_superuser_sets_role_and_permissions(self):
        user = User.objects.create_superuser(
            email="root@example.com",
            password="StrongPass123!",
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, User.Role.SUPER_ADMIN)


class AuthenticationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="login@example.com",
            password="StrongPass123!",
            role=User.Role.ISP_ADMIN,
        )

    def test_jwt_login_returns_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "login@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_dashboard_requires_authentication(self):
        response = self.client.get("/api/tenants/dashboard/")
        self.assertEqual(response.status_code, 401)


class TenantRegistrationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_registration_creates_tenant_and_isp_admin(self):
        response = self.client.post(
            "/api/tenants/register/",
            {
                "tenant_name": "VICOM Test ISP",
                "email": "owner@vicom.test",
                "phone_number": "+254700000000",
                "admin_name": "Test Admin",
                "password": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        tenant = Tenant.objects.get(email="owner@vicom.test")
        user = User.objects.get(email="owner@vicom.test")
        self.assertEqual(user.tenant_id, tenant.id)
        self.assertEqual(user.role, User.Role.ISP_ADMIN)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(email="owner@vicom.test", password="StrongPass123!")
        response = self.client.post(
            "/api/tenants/register/",
            {
                "tenant_name": "Duplicate ISP",
                "email": "owner@vicom.test",
                "phone_number": "+254700000001",
                "admin_name": "Duplicate Admin",
                "password": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

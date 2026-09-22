from django.test import TestCase
from rest_framework.test import APIRequestFactory

from .models import User
from .permissions import IsSuperAdmin, IsTenantAdmin, IsTenantUser
from tenants.models import Tenant


class PermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.tenant = Tenant.objects.create(
            name="Permission ISP",
            slug="permission-isp",
            email="permission@example.com",
            phone_number="+254700000020",
        )

    def request_for(self, user):
        request = self.factory.get("/api/test/")
        request.user = user
        return request

    def test_super_admin_requires_superuser_flag(self):
        role_only = User.objects.create_user(
            email="roleonly@example.com",
            password="StrongPass123!",
            role=User.Role.SUPER_ADMIN,
        )
        self.assertFalse(IsSuperAdmin().has_permission(self.request_for(role_only), None))

        admin = User.objects.create_superuser(
            email="super@example.com",
            password="StrongPass123!",
        )
        self.assertTrue(IsSuperAdmin().has_permission(self.request_for(admin), None))

    def test_tenant_admin_requires_isp_admin_and_tenant(self):
        admin = User.objects.create_user(
            email="isp@example.com",
            password="StrongPass123!",
            role=User.Role.ISP_ADMIN,
            tenant=self.tenant,
        )
        self.assertTrue(IsTenantAdmin().has_permission(self.request_for(admin), None))

        staff = User.objects.create_user(
            email="staff@example.com",
            password="StrongPass123!",
            role=User.Role.ISP_STAFF,
            tenant=self.tenant,
        )
        self.assertFalse(IsTenantAdmin().has_permission(self.request_for(staff), None))

    def test_tenant_user_requires_tenant(self):
        staff = User.objects.create_user(
            email="staff2@example.com",
            password="StrongPass123!",
            role=User.Role.ISP_STAFF,
            tenant=self.tenant,
        )
        self.assertTrue(IsTenantUser().has_permission(self.request_for(staff), None))

        customer = User.objects.create_user(
            email="customer@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.assertFalse(IsTenantUser().has_permission(self.request_for(customer), None))

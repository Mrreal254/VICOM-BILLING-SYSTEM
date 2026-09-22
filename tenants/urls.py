from django.urls import path

from .admin_api import SuperAdminTenantListView, SuperAdminTenantStatusView
from .views import TenantDashboardView, TenantRegistrationView

urlpatterns = [
    path("register/", TenantRegistrationView.as_view(), name="tenant-register"),
    path("dashboard/", TenantDashboardView.as_view(), name="tenant-dashboard"),
    path("admin/", SuperAdminTenantListView.as_view(), name="superadmin-tenant-list"),
    path("admin/<uuid:tenant_id>/status/", SuperAdminTenantStatusView.as_view(), name="superadmin-tenant-status"),
]

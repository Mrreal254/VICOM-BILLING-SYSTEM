from django.urls import path

from .views import TenantDashboardView, TenantRegistrationView

urlpatterns = [
    path("register/", TenantRegistrationView.as_view(), name="tenant-register"),
    path("dashboard/", TenantDashboardView.as_view(), name="tenant-dashboard"),
]

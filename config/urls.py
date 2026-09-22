from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .health import health_check


def root(request):
    return JsonResponse({
        "name": "VICOM Billing System",
        "status": "online",
        "phase": 1,
        "api": "/api/",
        "health": "/health/",
    })


urlpatterns = [
    path("", root, name="root"),
    path("health/", health_check, name="health"),
    path("admin/", admin.site.urls),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/tenants/", include("tenants.urls")),
]

from django.db.models import Count
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from .models import Tenant


class SuperAdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Role.SUPER_ADMIN:
            return Response({"detail": "Super Admin access required."}, status=status.HTTP_403_FORBIDDEN)

        counts = Tenant.objects.values("status").annotate(total=Count("id"))
        by_status = {row["status"]: row["total"] for row in counts}
        recent = Tenant.objects.order_by("-created_at")[:10]
        return Response({
            "tenants": {
                "total": Tenant.objects.count(),
                "active": by_status.get(Tenant.Status.ACTIVE, 0),
                "pending": by_status.get(Tenant.Status.PENDING, 0),
                "suspended": by_status.get(Tenant.Status.SUSPENDED, 0),
            },
            "recent_registrations": [
                {
                    "id": str(t.id),
                    "name": t.name,
                    "email": t.email,
                    "status": t.status,
                    "created_at": t.created_at,
                }
                for t in recent
            ],
        })


class IspAdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Role.ISP_ADMIN:
            return Response({"detail": "ISP Admin access required."}, status=status.HTTP_403_FORBIDDEN)
        tenant = request.user.tenant
        if tenant is None:
            return Response({"detail": "No tenant is assigned to this user."}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "tenant": {
                "id": str(tenant.id),
                "name": tenant.name,
                "slug": tenant.slug,
                "email": tenant.email,
                "phone_number": tenant.phone_number,
                "status": tenant.status,
                "currency": tenant.currency,
                "timezone": tenant.timezone,
            },
            "admin": {
                "id": str(request.user.id),
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "role": request.user.role,
            },
        })

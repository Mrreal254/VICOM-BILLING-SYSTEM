from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from .models import Tenant
from .serializers import TenantRegistrationSerializer


class TenantRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TenantRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant, user = serializer.save()
        return Response(
            {
                "message": "Tenant registered successfully.",
                "tenant": {"id": str(tenant.id), "name": tenant.name, "status": tenant.status},
                "user": {"id": str(user.id), "email": user.email, "role": user.role},
            },
            status=status.HTTP_201_CREATED,
        )


class TenantDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = request.user.tenant
        if tenant is None and request.user.role != User.Role.SUPER_ADMIN:
            return Response({"detail": "No tenant is assigned to this user."}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "tenant": None if tenant is None else {"id": str(tenant.id), "name": tenant.name, "status": tenant.status},
            "user": {"email": request.user.email, "role": request.user.role},
        })


class SuperAdminTenantListView(APIView):
    permission_classes = [IsAuthenticated]

    def _check_super_admin(self, request):
        return request.user.role == User.Role.SUPER_ADMIN

    def get(self, request):
        if not self._check_super_admin(request):
            return Response({"detail": "Super Admin access required."}, status=status.HTTP_403_FORBIDDEN)
        status_filter = request.query_params.get("status")
        tenants = Tenant.objects.all().order_by("name")
        if status_filter:
            tenants = tenants.filter(status=status_filter)
        return Response({
            "count": tenants.count(),
            "results": [
                {
                    "id": str(t.id),
                    "name": t.name,
                    "slug": t.slug,
                    "email": t.email,
                    "phone_number": t.phone_number,
                    "status": t.status,
                    "currency": t.currency,
                    "timezone": t.timezone,
                }
                for t in tenants
            ],
        })


class SuperAdminTenantStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, tenant_id):
        if request.user.role != User.Role.SUPER_ADMIN:
            return Response({"detail": "Super Admin access required."}, status=status.HTTP_403_FORBIDDEN)
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return Response({"detail": "Tenant not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        valid_statuses = {choice for choice, _ in Tenant.Status.choices}
        if new_status not in valid_statuses:
            return Response(
                {"detail": "Invalid status.", "allowed": sorted(valid_statuses)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tenant.status = new_status
        tenant.save(update_fields=["status", "updated_at"])
        return Response({"id": str(tenant.id), "name": tenant.name, "status": tenant.status})

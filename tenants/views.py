from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
        if tenant is None and request.user.role != request.user.Role.SUPER_ADMIN:
            return Response({"detail": "No tenant is assigned to this user."}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "tenant": None if tenant is None else {"id": str(tenant.id), "name": tenant.name, "status": tenant.status},
            "user": {"email": request.user.email, "role": request.user.role},
        })

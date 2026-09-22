from django.db import transaction
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsSuperAdmin
from .models import Tenant


class TenantAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = (
            "id", "name", "slug", "email", "phone_number",
            "status", "currency", "timezone", "created_at", "updated_at",
        )
        read_only_fields = fields


class TenantStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ("status",)

    def validate_status(self, value):
        allowed = {choice for choice, _ in Tenant.Status.choices}
        if value not in allowed:
            raise serializers.ValidationError("Invalid tenant status.")
        return value


class SuperAdminTenantListView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        queryset = Tenant.objects.all()
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        return Response({"count": queryset.count(), "results": TenantAdminSerializer(queryset, many=True).data})


class SuperAdminTenantStatusView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @transaction.atomic
    def patch(self, request, tenant_id):
        try:
            tenant = Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return Response({"detail": "Tenant not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TenantStatusSerializer(tenant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TenantAdminSerializer(tenant).data)

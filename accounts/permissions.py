from rest_framework.permissions import BasePermission

from .models import User


class IsSuperAdmin(BasePermission):
    """Allow only VICOM platform super administrators."""

    message = "Super Admin access is required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.SUPER_ADMIN
            and request.user.is_superuser
        )


class IsTenantAdmin(BasePermission):
    """Allow tenant administrators, with an assigned tenant."""

    message = "ISP Admin access is required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ISP_ADMIN
            and request.user.tenant_id
        )


class IsTenantUser(BasePermission):
    """Allow any authenticated user assigned to an ISP tenant."""

    message = "A tenant assignment is required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.tenant_id
        )

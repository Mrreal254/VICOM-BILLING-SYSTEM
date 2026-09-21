from django.contrib import admin

from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number", "status", "currency", "timezone", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("name", "email", "phone_number", "slug")
    readonly_fields = ("id", "created_at", "updated_at")

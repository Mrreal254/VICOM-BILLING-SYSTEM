from django.contrib import admin

from .models import Customer, Package, Subscription


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer_number", "full_name", "tenant", "phone_number", "status")
    list_filter = ("status", "tenant")
    search_fields = ("customer_number", "full_name", "email", "phone_number")


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "price", "duration_days", "active")
    list_filter = ("active", "tenant")
    search_fields = ("name", "description")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("customer", "package", "tenant", "status", "start_date", "end_date")
    list_filter = ("status", "tenant", "auto_renew")
    search_fields = ("customer__full_name", "customer__customer_number", "package__name")

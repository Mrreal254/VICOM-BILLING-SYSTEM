from rest_framework import serializers

from .models import Customer, Package, Subscription


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "customer_number", "full_name", "email", "phone_number", "status", "address", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ["id", "name", "description", "price", "duration_days", "download_speed_mbps", "upload_speed_mbps", "active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "customer", "package", "status", "start_date", "end_date", "auto_renew", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify
from rest_framework import serializers

from .models import Tenant

User = get_user_model()


class TenantRegistrationSerializer(serializers.Serializer):
    tenant_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    admin_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        base_slug = slugify(validated_data["tenant_name"]) or "isp"
        slug = base_slug
        counter = 2
        while Tenant.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        tenant = Tenant.objects.create(
            name=validated_data["tenant_name"],
            slug=slug,
            email=validated_data["email"],
            phone_number=validated_data["phone_number"],
            status=Tenant.Status.ACTIVE,
        )
        first, *last = validated_data["admin_name"].split(" ", 1)
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=first,
            last_name=last[0] if last else "",
            role=User.Role.ISP_ADMIN,
            tenant=tenant,
            is_staff=True,
        )
        return tenant, user

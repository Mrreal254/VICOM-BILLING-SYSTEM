import uuid

from django.db import models


class Tenant(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"
        PENDING = "PENDING", "Pending"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    currency = models.CharField(max_length=3, default="KES")
    timezone = models.CharField(max_length=64, default="Africa/Nairobi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.name

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Customer(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"
        PENDING = "PENDING", "Pending"

    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="customers")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="customer_profile")
    customer_number = models.CharField(max_length=32)
    full_name = models.CharField(max_length=160)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=32)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    address = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["tenant", "customer_number"], name="unique_customer_number_per_tenant")]

    def __str__(self):
        return f"{self.customer_number} - {self.full_name}"


class Package(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="packages")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    duration_days = models.PositiveIntegerField(default=30)
    download_speed_mbps = models.PositiveIntegerField(default=0)
    upload_speed_mbps = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["tenant", "name"], name="unique_package_name_per_tenant")]

    def __str__(self):
        return self.name


class Subscription(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"
        SUSPENDED = "SUSPENDED", "Suspended"
        CANCELLED = "CANCELLED", "Cancelled"

    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="subscriptions")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="subscriptions")
    package = models.ForeignKey(Package, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer} / {self.package}"

    def activate(self, *, start_date=None):
        start = start_date or self.start_date or timezone.now()
        self.start_date = start
        self.end_date = start + timezone.timedelta(days=self.package.duration_days)
        self.status = self.Status.ACTIVE
        self.save(update_fields=["start_date", "end_date", "status", "updated_at"])

    def suspend(self):
        self.status = self.Status.SUSPENDED
        self.save(update_fields=["status", "updated_at"])

    def cancel(self):
        self.status = self.Status.CANCELLED
        self.auto_renew = False
        self.save(update_fields=["status", "auto_renew", "updated_at"])

    def mark_expired_if_due(self):
        if self.status == self.Status.ACTIVE and self.end_date and self.end_date <= timezone.now():
            self.status = self.Status.EXPIRED
            self.save(update_fields=["status", "updated_at"])
            return True
        return False

from .invoice_models import Invoice  # noqa: E402,F401
from .payment_models import PaymentTransaction  # noqa: E402,F401

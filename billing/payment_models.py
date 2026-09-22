from decimal import Decimal

from django.db import models


class PaymentTransaction(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Successful"
        FAILED = "FAILED", "Failed"
        REVERSED = "REVERSED", "Reversed"

    class Method(models.TextChoices):
        MPESA = "MPESA", "M-Pesa"
        CASH = "CASH", "Cash"
        BANK = "BANK", "Bank"
        OTHER = "OTHER", "Other"

    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="payment_transactions")
    invoice = models.ForeignKey("billing.Invoice", on_delete=models.PROTECT, related_name="payments")
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.MPESA)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_successful(self, paid_at=None):
        from django.utils import timezone
        self.status = self.Status.SUCCESS
        self.paid_at = paid_at or timezone.now()
        self.save(update_fields=["status", "paid_at", "updated_at"])
        self.invoice.amount_paid = min(self.invoice.total, self.invoice.amount_paid + self.amount)
        if self.invoice.amount_paid >= self.invoice.total:
            self.invoice.status = self.invoice.Status.PAID
        elif self.invoice.amount_paid > 0:
            self.invoice.status = self.invoice.Status.PARTIALLY_PAID
        self.invoice.save(update_fields=["amount_paid", "status", "updated_at"])

from decimal import Decimal

from django.db import models


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ISSUED = "ISSUED", "Issued"
        PAID = "PAID", "Paid"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially paid"
        OVERDUE = "OVERDUE", "Overdue"
        VOID = "VOID", "Void"

    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="invoices")
    customer = models.ForeignKey("billing.Customer", on_delete=models.PROTECT, related_name="invoices")
    subscription = models.ForeignKey("billing.Subscription", on_delete=models.PROTECT, related_name="invoices", null=True, blank=True)
    invoice_number = models.CharField(max_length=40)
    issue_date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issue_date", "-created_at"]
        constraints = [models.UniqueConstraint(fields=["tenant", "invoice_number"], name="unique_invoice_number_per_tenant")]

    @property
    def balance_due(self):
        return max(self.total - self.amount_paid, Decimal("0.00"))

    def recalculate_total(self):
        self.total = self.subtotal + self.tax
        self.save(update_fields=["total", "updated_at"])

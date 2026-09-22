from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_number", models.CharField(max_length=40)),
                ("issue_date", models.DateField()),
                ("due_date", models.DateField()),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("tax", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("amount_paid", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("status", models.CharField(choices=[("DRAFT", "Draft"), ("ISSUED", "Issued"), ("PAID", "Paid"), ("PARTIALLY_PAID", "Partially paid"), ("OVERDUE", "Overdue"), ("VOID", "Void")], default="DRAFT", max_length=20)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="billing.customer")),
                ("subscription", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="billing.subscription")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invoices", to="tenants.tenant")),
            ],
            options={"ordering": ["-issue_date", "-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="invoice",
            constraint=models.UniqueConstraint(fields=("tenant", "invoice_number"), name="unique_invoice_number_per_tenant"),
        ),
        migrations.CreateModel(
            name="PaymentTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference", models.CharField(max_length=100, unique=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("method", models.CharField(choices=[("MPESA", "M-Pesa"), ("CASH", "Cash"), ("BANK", "Bank"), ("OTHER", "Other")], default="MPESA", max_length=20)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("SUCCESS", "Successful"), ("FAILED", "Failed"), ("REVERSED", "Reversed")], default="PENDING", max_length=20)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payments", to="billing.invoice")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payment_transactions", to="tenants.tenant")),
            ],
        ),
    ]

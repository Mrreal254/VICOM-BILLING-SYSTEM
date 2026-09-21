import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tenant",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=150)),
                ("slug", models.SlugField(max_length=160, unique=True)),
                ("email", models.EmailField(max_length=254)),
                ("phone_number", models.CharField(max_length=20)),
                ("status", models.CharField(choices=[("ACTIVE", "Active"), ("SUSPENDED", "Suspended"), ("PENDING", "Pending")], default="PENDING", max_length=20)),
                ("currency", models.CharField(default="KES", max_length=3)),
                ("timezone", models.CharField(default="Africa/Nairobi", max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="tenant",
            index=models.Index(fields=["status"], name="tenants_ten_status_9a4c2d_idx"),
        ),
        migrations.AddIndex(
            model_name="tenant",
            index=models.Index(fields=["email"], name="tenants_ten_email_8d4a3c_idx"),
        ),
    ]

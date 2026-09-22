from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction

from .invoice_models import Invoice


@transaction.atomic
def generate_subscription_invoice(subscription, *, tax=Decimal("0.00"), issue_date=None, due_days=7):
    issue_date = issue_date or date.today()
    due_date = issue_date + timedelta(days=due_days)
    subtotal = subscription.package.price
    invoice = Invoice.objects.create(
        tenant=subscription.tenant,
        customer=subscription.customer,
        subscription=subscription,
        invoice_number=_next_invoice_number(subscription.tenant_id, issue_date.year),
        issue_date=issue_date,
        due_date=due_date,
        subtotal=subtotal,
        tax=tax,
        total=subtotal + tax,
        status=Invoice.Status.ISSUED,
    )
    return invoice


def _next_invoice_number(tenant_id, year):
    prefix = f"INV-{year}-{tenant_id.hex[:8].upper()}-"
    count = Invoice.objects.filter(tenant_id=tenant_id, invoice_number__startswith=prefix).count() + 1
    return f"{prefix}{count:06d}"

from datetime import date, timedelta
from decimal import Decimal

from .invoice_models import Invoice
from .models import Subscription
from .platform_billing import platform_billing_summary


def generate_subscription_invoice(subscription, tax=Decimal("0.00"), due_days=7):
    if subscription.status not in {Subscription.Status.ACTIVE, Subscription.Status.PENDING}:
        raise ValueError("Only pending or active subscriptions can generate an invoice.")
    if subscription.tenant_id != subscription.customer.tenant_id or subscription.tenant_id != subscription.package.tenant_id:
        raise ValueError("Subscription, customer, package and invoice tenant must match.")

    issue_date = date.today()
    number = f"INV-{subscription.tenant_id}-{issue_date:%Y%m%d}-{subscription.id}"
    subtotal = subscription.package.price
    invoice, _ = Invoice.objects.get_or_create(
        tenant_id=subscription.tenant_id,
        invoice_number=number,
        defaults={
            "customer_id": subscription.customer_id,
            "subscription_id": subscription.id,
            "issue_date": issue_date,
            "due_date": issue_date + timedelta(days=due_days),
            "subtotal": subtotal,
            "tax": Decimal(str(tax)),
            "total": subtotal + Decimal(str(tax)),
            "status": Invoice.Status.ISSUED,
        },
    )
    return invoice


def generate_platform_invoice(tenant, hotspot_revenue, active_pppoe_subscribers, tax=Decimal("0.00"), due_days=7):
    summary = platform_billing_summary(hotspot_revenue, active_pppoe_subscribers)
    issue_date = date.today()
    number = f"VICOM-{tenant.id}-{issue_date:%Y%m%d}"
    subtotal = summary["total_platform_fee"]
    tax = Decimal(str(tax))
    invoice, _ = Invoice.objects.get_or_create(
        tenant=tenant,
        invoice_number=number,
        defaults={
            "issue_date": issue_date,
            "due_date": issue_date + timedelta(days=due_days),
            "subtotal": subtotal,
            "tax": tax,
            "total": subtotal + tax,
            "status": Invoice.Status.ISSUED,
            "notes": f"Hotspot revenue: {summary['hotspot_revenue']}; active PPPoE subscribers: {summary['active_pppoe_subscribers']}; hotspot fee: {summary['hotspot_fee']}; PPPoE fee: {summary['pppoe_fee']}",
        },
    )
    return invoice, summary

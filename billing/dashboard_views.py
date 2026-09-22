from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .invoice_models import Invoice
from .payment_models import PaymentTransaction
from .models import Customer, Subscription


class BillingDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = request.user.tenant
        invoices = Invoice.objects.filter(tenant=tenant)
        payments = PaymentTransaction.objects.filter(tenant=tenant, status=PaymentTransaction.Status.SUCCESS)
        subscriptions = Subscription.objects.filter(tenant=tenant)
        return Response({
            "customers": Customer.objects.filter(tenant=tenant).count(),
            "active_subscriptions": subscriptions.filter(status=Subscription.Status.ACTIVE).count(),
            "invoices": invoices.count(),
            "issued_total": invoices.filter(status=Invoice.Status.ISSUED).aggregate(total=Sum("total"))["total"] or 0,
            "outstanding": sum((invoice.balance_due for invoice in invoices.exclude(status=Invoice.Status.PAID)), 0),
            "collected": payments.aggregate(total=Sum("amount"))["total"] or 0,
            "successful_payments": payments.count(),
        })

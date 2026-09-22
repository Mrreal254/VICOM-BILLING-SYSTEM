from decimal import Decimal

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .invoice_models import Invoice
from .invoice_services import generate_platform_invoice, generate_subscription_invoice
from .models import Subscription


class PlatformInvoiceGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant = getattr(request.user, "tenant", None)
        if tenant is None:
            return Response({"detail": "No tenant is assigned."}, status=status.HTTP_403_FORBIDDEN)
        try:
            invoice, summary = generate_platform_invoice(
                tenant,
                request.data.get("hotspot_revenue", 0),
                request.data.get("active_pppoe_subscribers", 0),
                Decimal(str(request.data.get("tax", "0.00"))),
            )
        except (ValueError, TypeError, ArithmeticError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "subtotal": str(invoice.subtotal),
            "tax": str(invoice.tax),
            "total": str(invoice.total),
            "balance_due": str(invoice.balance_due),
            "hotspot_fee": str(summary["hotspot_fee"]),
            "pppoe_fee": str(summary["pppoe_fee"]),
            "total_platform_fee": str(summary["total_platform_fee"]),
        }, status=status.HTTP_201_CREATED)


class SubscriptionInvoiceGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, subscription_id):
        subscription = Subscription.objects.filter(id=subscription_id, tenant=request.user.tenant).first()
        if subscription is None:
            return Response({"detail": "Subscription not found."}, status=404)
        try:
            invoice = generate_subscription_invoice(subscription, Decimal(str(request.data.get("tax", "0.00"))))
        except (ValueError, TypeError, ArithmeticError) as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "total": str(invoice.total),
            "balance_due": str(invoice.balance_due),
            "status": invoice.status,
        }, status=201)

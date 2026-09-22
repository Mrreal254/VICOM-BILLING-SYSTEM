from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .invoice_models import Invoice
from .payment_models import PaymentTransaction


class InvoicePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id, tenant=request.user.tenant)
        amount = Decimal(str(request.data.get("amount", "0")))
        if amount <= 0:
            return Response({"detail": "Payment amount must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)
        if amount > invoice.balance_due:
            return Response({"detail": "Payment exceeds invoice balance."}, status=status.HTTP_400_BAD_REQUEST)

        reference = request.data.get("reference")
        if not reference:
            return Response({"detail": "Payment reference is required."}, status=status.HTTP_400_BAD_REQUEST)
        if PaymentTransaction.objects.filter(reference=reference).exists():
            return Response({"detail": "Payment reference already exists."}, status=status.HTTP_400_BAD_REQUEST)

        payment = PaymentTransaction.objects.create(
            tenant=invoice.tenant,
            invoice=invoice,
            reference=reference,
            amount=amount,
            method=request.data.get("method", PaymentTransaction.Method.MPESA),
            status=PaymentTransaction.Status.PENDING,
            metadata=request.data.get("metadata", {}),
        )
        return Response({"id": payment.id, "reference": payment.reference, "amount": payment.amount, "status": payment.status}, status=status.HTTP_201_CREATED)


class PaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        payment = get_object_or_404(PaymentTransaction, id=payment_id, tenant=request.user.tenant)
        if payment.status == PaymentTransaction.Status.SUCCESS:
            return Response({"detail": "Payment already processed.", "payment_id": payment.id})
        if payment.status != PaymentTransaction.Status.PENDING:
            return Response({"detail": "Only pending payments can be completed."}, status=status.HTTP_400_BAD_REQUEST)
        payment.mark_successful()
        return Response({
            "payment_id": payment.id,
            "status": payment.status,
            "invoice_status": payment.invoice.status,
            "amount_paid": payment.invoice.amount_paid,
            "balance_due": payment.invoice.balance_due,
        })

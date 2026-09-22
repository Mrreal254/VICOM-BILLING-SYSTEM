from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription


class SubscriptionLifecycleView(APIView):
    permission_classes = [IsAuthenticated]

    def get_subscription(self, request, subscription_id):
        return Subscription.objects.filter(
            tenant=request.user.tenant_id,
            id=subscription_id,
        ).select_related("customer", "package").first()

    def patch(self, request, subscription_id):
        subscription = self.get_subscription(request, subscription_id)
        if subscription is None:
            return Response({"detail": "Subscription not found."}, status=404)

        action = request.data.get("action")
        if action == "activate":
            subscription.activate()
        elif action == "suspend":
            subscription.suspend()
        elif action == "cancel":
            subscription.cancel()
        elif action == "expire_if_due":
            subscription.mark_expired_if_due()
        else:
            return Response(
                {"detail": "Invalid lifecycle action.", "allowed": ["activate", "suspend", "cancel", "expire_if_due"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            "id": subscription.id,
            "status": subscription.status,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "auto_renew": subscription.auto_renew,
        })

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription
from .serializers import SubscriptionSerializer


class SubscriptionLifecycleView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, subscription_id):
        subscription = get_object_or_404(
            Subscription,
            id=subscription_id,
            tenant=request.user.tenant,
        )
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

        return Response(SubscriptionSerializer(subscription).data)

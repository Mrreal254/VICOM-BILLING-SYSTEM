from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from .models import Customer, Package, Subscription
from .serializers import CustomerSerializer, PackageSerializer, SubscriptionSerializer


class TenantScopedMixin:
    def tenant(self, request):
        return request.user.tenant

    def require_tenant(self, request):
        tenant = self.tenant(request)
        if tenant is None:
            return Response({"detail": "No tenant is assigned to this user."}, status=status.HTTP_403_FORBIDDEN)
        return tenant


class CustomerListCreateView(TenantScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = self.require_tenant(request)
        if not isinstance(tenant, object):
            return tenant
        customers = Customer.objects.filter(tenant=tenant)
        return Response(CustomerSerializer(customers, many=True).data)

    def post(self, request):
        tenant = self.require_tenant(request)
        if not isinstance(tenant, object):
            return tenant
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save(tenant=tenant)
        return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)


class CustomerDetailView(TenantScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, customer_id):
        return Customer.objects.filter(tenant=request.user.tenant, id=customer_id).first()

    def get(self, request, customer_id):
        customer = self.get_object(request, customer_id)
        if customer is None:
            return Response({"detail": "Customer not found."}, status=404)
        return Response(CustomerSerializer(customer).data)

    def patch(self, request, customer_id):
        customer = self.get_object(request, customer_id)
        if customer is None:
            return Response({"detail": "Customer not found."}, status=404)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, customer_id):
        customer = self.get_object(request, customer_id)
        if customer is None:
            return Response({"detail": "Customer not found."}, status=404)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PackageListCreateView(TenantScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = self.require_tenant(request)
        if not isinstance(tenant, object):
            return tenant
        return Response(PackageSerializer(Package.objects.filter(tenant=tenant), many=True).data)

    def post(self, request):
        tenant = self.require_tenant(request)
        if not isinstance(tenant, object):
            return tenant
        serializer = PackageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        package = serializer.save(tenant=tenant)
        return Response(PackageSerializer(package).data, status=201)


class SubscriptionListCreateView(TenantScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = self.require_tenant(request)
        if not isinstance(tenant, object):
            return tenant
        return Response(SubscriptionSerializer(Subscription.objects.filter(tenant=tenant), many=True).data)

    def post(self, request):
        tenant = self.require_tenant(request)
        if not isinstance(tenant, object):
            return tenant
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer_id = serializer.validated_data["customer"].id
        package_id = serializer.validated_data["package"].id
        if not Customer.objects.filter(id=customer_id, tenant=tenant).exists() or not Package.objects.filter(id=package_id, tenant=tenant).exists():
            return Response({"detail": "Customer and package must belong to the current tenant."}, status=400)
        subscription = serializer.save(tenant=tenant)
        return Response(SubscriptionSerializer(subscription).data, status=201)

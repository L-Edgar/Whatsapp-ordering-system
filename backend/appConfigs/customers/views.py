from django.db.models import Count
from rest_framework import viewsets, permissions
from .models import Customer
from .serializers import CustomerSerializer

class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        business = self.request.user.businesses.first()
        return (
            Customer.objects.filter(business=business)
            .annotate(orders_count=Count("orders"))
            .order_by("-created_at")
        )
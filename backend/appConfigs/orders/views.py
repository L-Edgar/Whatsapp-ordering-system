# orders/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer


def _business_for(user):
    return user.businesses.first()


#@api_view(['GET','PUT','POST'])
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch"]  # orders are created via the checkout flow, not directly

    def get_queryset(self):
        return Order.objects.filter(business=_business_for(self.request.user)).order_by("-created_at")

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Invalid status."}, status=400)
        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)
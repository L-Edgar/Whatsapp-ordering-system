from rest_framework import viewsets, permissions
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


def _business_for(user):
    # single-business-per-owner for now; adjust when staff/multi-business lands
    return user.businesses.first()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(business=_business_for(self.request.user))

    def perform_create(self, serializer):
        serializer.save(business=_business_for(self.request.user))


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(business=_business_for(self.request.user))

    def perform_create(self, serializer):
        serializer.save(business=_business_for(self.request.user))
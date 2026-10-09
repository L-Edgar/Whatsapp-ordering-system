from rest_framework import viewsets, permissions
from .models import Business
from .serializers import BusinessSerializer, BusinessRegistrationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class BusinessViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Business.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
class RegisterBusinessView(APIView):
    permission_classes = []  # public

    def post(self, request):
        serializer = BusinessRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        business = serializer.save()
        return Response({"business_id": business.id, "name": business.name}, status=status.HTTP_201_CREATED)
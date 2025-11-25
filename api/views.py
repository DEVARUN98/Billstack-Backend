# views.py
from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import InventoryItem
from .serializers import UserSerializer, InventoryItemSerializer
from .permissions import IsSuperUserOrSelf, IsOwnerOrSuperUser
from rest_framework.permissions import IsAuthenticated

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class AdminOnlyAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token_key = response.data.get('token')
        if token_key:
            token = Token.objects.get(key=token_key)
            if not token.user.is_staff:
                return Response({"error": "User is not admin"}, status=403)
            return Response({'token': token.key})
        return response

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSuperUserOrSelf]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)

class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSuperUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return InventoryItem.objects.all()
        return InventoryItem.objects.filter(user=user)

    def perform_create(self, serializer):
        # Ensure inventory item is linked to the current user
        serializer.save(user=self.request.user)

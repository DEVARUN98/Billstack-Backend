# views.py
from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import InventoryItem, UserProfile, Customers, Products,Invoices,InvoiceNew
from .serializers import UserSerializer, InventoryItemSerializer,CustomersSerializer,ProductsSerializer,InvoicesSerializer,InvoiceNewSerializer
from .permissions import IsSuperUserOrSelf, IsOwnerOrSuperUser
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

# FOR SESSION BASED LOGIN AND LOGOUT

from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes,action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from .auth import CsrfExemptSessionAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.authentication import TokenAuthentication

# Session-based login (no tokens needed)
# @csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def session_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return Response({
            'message': 'Login successful',
            'is_admin': user.is_staff or user.is_superuser,
            'username': user.username
        })
    return Response({'error': 'Invalid credentials'}, status=400)

# @csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])

@permission_classes([AllowAny])
def session_logout(request):
    logout(request)
    return Response({'message': 'Logged out successfully'})

# Session check endpoint
@csrf_exempt
@api_view(['GET'])
def session_status(request):
    if request.user.is_authenticated:
        return Response({
            'is_authenticated': True,
            'is_admin': request.user.is_staff or request.user.is_superuser,
            'username': request.user.username
        })
    return Response({'is_authenticated': False})


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


class CustomersViewSet(viewsets.ModelViewSet):
    serializer_class = CustomersSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSuperUser]
    authentication_classes = [CsrfExemptSessionAuthentication,TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Customers.objects.all()
        return Customers.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProductsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductsSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSuperUser]
    authentication_classes = [CsrfExemptSessionAuthentication,TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Products.objects.all()
        return Products.objects.filter(user=user)   

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class InvoicesViewSet(viewsets.ModelViewSet):
    serializer_class = InvoicesSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSuperUser]
    authentication_classes = [CsrfExemptSessionAuthentication,TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Invoices.objects.all()
        return Invoices.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InvoicesNewViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceNewSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return InvoiceNew.objects.all()
        return InvoiceNew.objects.filter(user=user)

    def perform_create(self, serializer):
        invoice = serializer.save(user=self.request.user)
        
        # Decrease inventory (YOUR EXISTING CODE)
        for item in invoice.items:
            try:
                product = Products.objects.get(
                    product_name=item['name'], 
                    user=self.request.user
                )
                product.product_quantity -= item['qty']
                product.product_quantity = max(0, product.product_quantity)
                product.save()
            except Products.DoesNotExist:
                pass

    @action(detail=False, methods=['get'])
    def customers(self, request):
        """Get unique customers from user's invoices"""
        user = request.user
        customers = InvoiceNew.objects.filter(user=user).values('customer_name', 'phone').annotate(
            total_invoices=Count('id'),
            total_spent=Sum('total')
        ).distinct().order_by('customer_name')
        return Response(list(customers))

    # 👈 NEW: Add customer endpoint
    @action(detail=False, methods=['post'])
    def add_customer(self, request):
        """Add new customer (minimal invoice record for tracking)"""
        user = request.user
        customer_name = request.data.get('customer_name', '').strip()
        phone = request.data.get('phone', '').strip()
        
        if not customer_name or not phone:
            return Response({'error': 'customer_name and phone required'}, status=400)
        
        # Check if customer already exists
        if InvoiceNew.objects.filter(
            user=user, 
            customer_name__iexact=customer_name, 
            phone=phone
        ).exists():
            return Response({'error': 'Customer already exists'}, status=400)
        
        # Create minimal invoice record
        invoice = InvoiceNew.objects.create(
            user=user,
            customer_name=customer_name,
            phone=phone,
            items=[],  # empty
            subtotal=0,
            gst=0,
            discount=0,
            total=0
        )
        
        return Response({
            'message': 'Customer added successfully',
            'customer': {
                'customer_name': customer_name,
                'phone': phone,
                'total_invoices': 0,
                'total_spent': '0.00'
            }
        })
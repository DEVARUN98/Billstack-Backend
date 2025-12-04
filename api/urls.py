# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserViewSet, InventoryViewSet,
        AdminOnlyAuthToken, CustomersViewSet, ProductsViewSet,InvoicesViewSet,InvoicesNewViewSet,
        session_login, session_logout, session_status)   # FOR SESSION BASED LOGIN AND LOGOUT
from rest_framework.authtoken import views


router = DefaultRouter()
router.register(r'users', UserViewSet,basename ='user')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'customers', CustomersViewSet, basename='customers')
router.register(r'products', ProductsViewSet, basename='products')
router.register(r'invoices', InvoicesViewSet, basename='invoices')
router.register(r'invoicesnew', InvoicesNewViewSet, basename='invoicesnew')

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', AdminOnlyAuthToken.as_view(), name='api_token_auth'),

    path('login/', session_login, name='session_login'),          # ← NEW
    path('logout/', session_logout, name='session_logout'),       # ← NEW
    path('session-status/', session_status, name='session_status'), # ← NEW


]

# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, InventoryViewSet,AdminOnlyAuthToken
from rest_framework.authtoken import views


router = DefaultRouter()
router.register(r'users', UserViewSet,basename ='user')
router.register(r'inventory', InventoryViewSet, basename='inventory')

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', AdminOnlyAuthToken.as_view(), name='api_token_auth'),

]

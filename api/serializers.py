# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, InventoryItem

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'item_name', 'quantity']

class UserProfileSerializer(serializers.ModelSerializer):
    expiry_date = serializers.DateField()

    class Meta:
        model = UserProfile
        fields = ['expiry_date']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=True)
    inventory = InventoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'profile', 'inventory']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.filter(user=user).update(expiry_date=profile_data['expiry_date'])
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        instance.username = validated_data.get('username', instance.username)
        instance.save()
        if profile_data:
            profile = instance.userprofile
            profile.expiry_date = profile_data.get('expiry_date', profile.expiry_date)
            profile.save()
        return instance

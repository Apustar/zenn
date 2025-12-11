from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'bio', 'website', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserPublicSerializer(serializers.ModelSerializer):
    """公开用户信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'bio', 'website']


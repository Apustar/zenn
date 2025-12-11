from rest_framework import serializers
from .models import Moment, MomentLike
from users.serializers import UserPublicSerializer


class MomentSerializer(serializers.ModelSerializer):
    """瞬间序列化器"""
    author = UserPublicSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Moment
        fields = [
            'id', 'content', 'author', 'images', 'location',
            'visibility', 'likes_count', 'is_liked', 'comments_count',
            'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'likes_count', 'comments_count', 'created_at', 'updated_at']

    def get_likes_count(self, obj):
        return obj.likes

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return MomentLike.objects.filter(moment=obj, user=request.user).exists()
        return False


class MomentCreateSerializer(serializers.ModelSerializer):
    """瞬间创建序列化器"""
    class Meta:
        model = Moment
        fields = ['content', 'images', 'location', 'visibility']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


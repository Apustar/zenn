from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Comment, CommentLike
from users.serializers import UserPublicSerializer


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    author = UserPublicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'content', 'parent', 'replies', 'likes_count',
            'is_liked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_replies(self, obj):
        replies = obj.get_replies()
        serializer = CommentSerializer(replies, many=True, context=self.context)
        return serializer.data

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommentLike.objects.filter(comment=obj, user=request.user).exists()
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    """评论创建序列化器"""
    class Meta:
        model = Comment
        fields = ['content', 'parent']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        # 从 context 中获取 content_object
        content_object = self.context.get('content_object')
        if content_object:
            validated_data['content_type'] = ContentType.objects.get_for_model(content_object.__class__)
            validated_data['object_id'] = content_object.pk
        return super().create(validated_data)


from rest_framework import serializers
from .models import Post, PostLike
from categories.serializers import CategorySerializer
from tags.serializers import TagSerializer
from users.serializers import UserPublicSerializer


class PostListSerializer(serializers.ModelSerializer):
    """文章列表序列化器"""
    author = UserPublicSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    word_count = serializers.SerializerMethodField()
    read_time = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'cover', 'author', 'category', 'tags',
            'is_top', 'views', 'likes', 'word_count', 'read_time', 'published_at', 'created_at'
        ]

    def get_word_count(self, obj):
        return obj.get_word_count()

    def get_read_time(self, obj):
        return obj.get_read_time()


class PostDetailSerializer(serializers.ModelSerializer):
    """文章详情序列化器"""
    author = UserPublicSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    word_count = serializers.SerializerMethodField()
    read_time = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'content_html', 'cover',
            'author', 'category', 'tags', 'status', 'is_top', 'is_original',
            'allow_comment', 'views', 'likes', 'is_liked', 'word_count', 'read_time',
            'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'views', 'likes', 'created_at', 'updated_at']

    def get_word_count(self, obj):
        return obj.get_word_count()

    def get_read_time(self, obj):
        return obj.get_read_time()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(post=obj, user=request.user).exists()
        return False


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """文章创建/更新序列化器"""
    class Meta:
        model = Post
        fields = [
            'title', 'slug', 'excerpt', 'content', 'cover', 'category', 'tags',
            'status', 'is_top', 'is_original', 'allow_comment', 'published_at'
        ]

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


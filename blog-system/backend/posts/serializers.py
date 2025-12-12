from rest_framework import serializers
from .models import Post, PostLike
from .utils import check_password_verified_in_session
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
    is_encrypted = serializers.BooleanField(read_only=True)
    is_password_verified = serializers.SerializerMethodField()
    preview_content_html = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'content_html', 'cover',
            'author', 'category', 'tags', 'status', 'is_top', 'is_original',
            'allow_comment', 'views', 'likes', 'is_liked', 'word_count', 'read_time',
            'is_encrypted', 'is_password_verified', 'preview_content_html',
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
    
    def get_is_password_verified(self, obj):
        """检查密码是否已验证"""
        request = self.context.get('request')
        if not obj.is_encrypted:
            return True  # 未加密的文章视为已验证
        if not request:
            return False
        
        # 管理员可以直接访问
        if request.user.is_authenticated and request.user.is_staff:
            return True
        
        # 检查session中是否已验证
        return check_password_verified_in_session(request, 'post', obj.id, obj.password_updated_at)
    
    def get_preview_content_html(self, obj):
        """获取预览内容（加密文章未验证时只显示前500字符）"""
        request = self.context.get('request')
        if not obj.is_encrypted:
            return None
        
        is_verified = self.get_is_password_verified(obj)
        if is_verified:
            return None  # 已验证，返回完整内容
        
        # 未验证，返回预览内容
        if obj.content_html:
            # 截取前500字符，尽量在段落或句子结束处截断
            preview = obj.content_html[:500]
            # 尝试在最后一个</p>或</div>处截断
            last_p = preview.rfind('</p>')
            last_div = preview.rfind('</div>')
            cut_point = max(last_p, last_div)
            if cut_point > 200:  # 确保有足够的内容
                preview = preview[:cut_point + (5 if last_p > last_div else 6)]
            return preview
        return None
    
    def to_representation(self, instance):
        """重写序列化方法，根据验证状态决定返回的内容"""
        data = super().to_representation(instance)
        
        # 如果是加密文章且未验证，隐藏完整内容
        if instance.is_encrypted and not data.get('is_password_verified'):
            data['content'] = None
            data['content_html'] = None
            # preview_content_html 已经在 get_preview_content_html 中设置
        
        return data


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """文章创建/更新序列化器"""
    class Meta:
        model = Post
        fields = [
            'title', 'slug', 'excerpt', 'content', 'cover', 'category', 'tags',
            'status', 'is_top', 'is_original', 'allow_comment', 'published_at',
            'is_encrypted', 'password'
        ]

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


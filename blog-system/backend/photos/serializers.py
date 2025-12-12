from rest_framework import serializers
from .models import Album, Photo
from .utils import check_password_verified_in_session
from users.serializers import UserPublicSerializer


class PhotoSerializer(serializers.ModelSerializer):
    """照片序列化器"""
    class Meta:
        model = Photo
        fields = ['id', 'title', 'image', 'description', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class AlbumSerializer(serializers.ModelSerializer):
    """相册序列化器"""
    author = UserPublicSerializer(read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)
    photos_count = serializers.SerializerMethodField()
    is_encrypted = serializers.BooleanField(read_only=True)
    is_password_verified = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id', 'name', 'slug', 'description', 'cover', 'author',
            'photos', 'photos_count', 'is_encrypted', 'is_password_verified',
            'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photos_count(self, obj):
        return obj.photos.count()
    
    def get_is_password_verified(self, obj):
        """检查密码是否已验证"""
        request = self.context.get('request')
        if not obj.is_encrypted:
            return True  # 未加密的相册视为已验证
        if not request:
            return False
        
        # 管理员可以直接访问
        if request.user.is_authenticated and request.user.is_staff:
            return True
        
        # 检查session中是否已验证
        return check_password_verified_in_session(request, 'album', obj.id, obj.password_updated_at)
    
    def to_representation(self, instance):
        """重写序列化方法，根据验证状态决定返回的照片"""
        data = super().to_representation(instance)
        
        # 如果是加密相册且未验证，隐藏照片
        if instance.is_encrypted and not data.get('is_password_verified'):
            data['photos'] = []
        
        return data


class AlbumCreateSerializer(serializers.ModelSerializer):
    """相册创建序列化器"""
    class Meta:
        model = Album
        fields = ['name', 'slug', 'description', 'cover', 'order', 'is_encrypted', 'password']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


from rest_framework import serializers
from .models import Album, Photo
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

    class Meta:
        model = Album
        fields = [
            'id', 'name', 'slug', 'description', 'cover', 'author',
            'photos', 'photos_count', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photos_count(self, obj):
        return obj.photos.count()


class AlbumCreateSerializer(serializers.ModelSerializer):
    """相册创建序列化器"""
    class Meta:
        model = Album
        fields = ['name', 'slug', 'description', 'cover', 'order']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


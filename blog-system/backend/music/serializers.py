from rest_framework import serializers
from .models import Music
from users.serializers import UserPublicSerializer


class MusicSerializer(serializers.ModelSerializer):
    """音乐序列化器"""
    author = UserPublicSerializer(read_only=True)
    audio_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Music
        fields = [
            'id', 'title', 'artist', 'album', 'audio_file', 'audio_url',
            'cover', 'cover_url', 'lyrics', 'duration', 'order',
            'is_published', 'author', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_audio_url(self, obj):
        """获取音频文件的完整URL"""
        if obj.audio_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.audio_file.url)
            return obj.audio_file.url
        return None

    def get_cover_url(self, obj):
        """获取封面图的完整URL"""
        if obj.cover:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover.url)
            return obj.cover.url
        return None


class MusicCreateSerializer(serializers.ModelSerializer):
    """音乐创建序列化器"""
    class Meta:
        model = Music
        fields = ['title', 'artist', 'album', 'audio_file', 'cover', 'lyrics', 'order', 'duration', 'is_published']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


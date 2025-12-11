from rest_framework import serializers
from .models import LinkCategory, Link


class LinkSerializer(serializers.ModelSerializer):
    """友链序列化器"""
    class Meta:
        model = Link
        fields = [
            'id', 'name', 'url', 'description', 'logo', 'category',
            'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LinkCategorySerializer(serializers.ModelSerializer):
    """友链分类序列化器"""
    links = serializers.SerializerMethodField()

    class Meta:
        model = LinkCategory
        fields = ['id', 'name', 'order', 'links', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_links(self, obj):
        """只返回可见的链接，并按顺序排序"""
        visible_links = obj.links.filter(is_visible=True).order_by('order', 'name')
        return LinkSerializer(visible_links, many=True).data


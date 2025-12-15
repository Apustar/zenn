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
        """管理员可以看到所有链接，普通用户只能看到可见的链接"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.is_staff:
            # 管理员查看所有链接
            links = obj.links.all().order_by('order', 'name')
        else:
            # 普通用户只看到可见的链接
            links = obj.links.filter(is_visible=True).order_by('order', 'name')
        return LinkSerializer(links, many=True).data


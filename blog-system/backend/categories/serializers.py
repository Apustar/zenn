from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    post_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'cover', 'parent', 'order', 'post_count', 'children', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data


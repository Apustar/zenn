from rest_framework import viewsets, permissions
from .models import LinkCategory, Link
from .serializers import LinkCategorySerializer, LinkSerializer


class LinkCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """友链分类视图集"""
    serializer_class = LinkCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # 禁用分页，直接返回数组

    def get_queryset(self):
        """返回所有有可见链接的分类"""
        # 只返回至少有一个可见链接的分类
        return LinkCategory.objects.filter(
            links__is_visible=True
        ).distinct().prefetch_related(
            'links'
        ).order_by('order', 'name')
    
    def list(self, request, *args, **kwargs):
        """确保只返回有可见链接的分类"""
        response = super().list(request, *args, **kwargs)
        # 由于禁用了分页，response.data 应该是列表
        if response.data and isinstance(response.data, list):
            # 过滤掉 links 为空数组的分类
            filtered_data = []
            for cat in response.data:
                if isinstance(cat, dict):
                    links = cat.get('links', [])
                    if links and len(links) > 0:
                        filtered_data.append(cat)
            response.data = filtered_data
        return response


class LinkViewSet(viewsets.ReadOnlyModelViewSet):
    """友链视图集"""
    queryset = Link.objects.filter(is_visible=True).select_related('category')
    serializer_class = LinkSerializer
    permission_classes = [permissions.AllowAny]

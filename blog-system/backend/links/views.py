from rest_framework import viewsets, permissions
from .models import LinkCategory, Link
from .serializers import LinkCategorySerializer, LinkSerializer


class LinkCategoryViewSet(viewsets.ModelViewSet):
    """友链分类视图集"""
    serializer_class = LinkCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # 禁用分页，直接返回数组

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        """管理员可以查看所有分类，普通用户只看到有可见链接的分类"""
        if self.request.user.is_authenticated and self.request.user.is_staff:
            # 管理员查看所有分类
            return LinkCategory.objects.all().prefetch_related('links').order_by('order', 'name')
        else:
            # 普通用户只返回至少有一个可见链接的分类
            return LinkCategory.objects.filter(
                links__is_visible=True
            ).distinct().prefetch_related(
                'links'
            ).order_by('order', 'name')
    
    def list(self, request, *args, **kwargs):
        """确保普通用户只返回有可见链接的分类"""
        response = super().list(request, *args, **kwargs)
        # 由于禁用了分页，response.data 应该是列表
        if response.data and isinstance(response.data, list) and not (request.user.is_authenticated and request.user.is_staff):
            # 过滤掉 links 为空数组的分类（仅对普通用户）
            filtered_data = []
            for cat in response.data:
                if isinstance(cat, dict):
                    links = cat.get('links', [])
                    if links and len(links) > 0:
                        filtered_data.append(cat)
            response.data = filtered_data
        return response


class LinkViewSet(viewsets.ModelViewSet):
    """友链视图集"""
    queryset = Link.objects.all().select_related('category')
    serializer_class = LinkSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        """管理员可以查看所有链接，普通用户只看到可见的"""
        queryset = Link.objects.all().select_related('category')
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(is_visible=True)
        return queryset

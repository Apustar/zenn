from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Music
from .serializers import MusicSerializer, MusicCreateSerializer


class MusicViewSet(viewsets.ModelViewSet):
    """音乐视图集"""
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # 禁用分页，直接返回数组
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MusicCreateSerializer
        return MusicSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """只返回已发布的音乐"""
        queryset = Music.objects.filter(is_published=True).select_related('author')
        
        # 管理员可以查看所有音乐
        if self.request.user.is_authenticated and self.request.user.is_staff:
            queryset = Music.objects.all().select_related('author')
        
        return queryset.order_by('order', '-created_at')
    
    def list(self, request, *args, **kwargs):
        """获取音乐列表"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """获取音乐详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)


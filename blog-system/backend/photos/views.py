from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from .models import Album, Photo
from .serializers import AlbumSerializer, AlbumCreateSerializer, PhotoSerializer
from .utils import verify_content_password, mark_password_verified_in_session


class AlbumViewSet(viewsets.ModelViewSet):
    """相册视图集"""
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AlbumCreateSerializer
        return AlbumSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """优化查询，确保照片按顺序返回"""
        queryset = Album.objects.all().select_related('author').prefetch_related(
            models.Prefetch('photos', queryset=Photo.objects.order_by('order', '-created_at'))
        )
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """获取相册详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify_password(self, request, slug=None):
        """验证相册密码"""
        album = self.get_object()
        
        if not album.is_encrypted:
            return Response({'error': '该相册未加密'}, status=status.HTTP_400_BAD_REQUEST)
        
        password = request.data.get('password')
        if not password:
            return Response({'error': '请输入密码'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证密码
        if verify_content_password(album.password, password):
            # 标记为已验证（使用密码更新时间）
            mark_password_verified_in_session(request, 'album', album.id, album.password_updated_at)
            return Response({'success': True, 'message': '密码验证成功'})
        else:
            return Response({'error': '密码错误'}, status=status.HTTP_400_BAD_REQUEST)


class PhotoViewSet(viewsets.ModelViewSet):
    """照片视图集"""
    queryset = Photo.objects.all().select_related('album')
    serializer_class = PhotoSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django.db.models import Q
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
        """优化查询，确保照片按顺序返回，支持搜索"""
        queryset = Album.objects.all().select_related('author').prefetch_related(
            models.Prefetch('photos', queryset=Photo.objects.order_by('order', '-created_at'))
        )
        
        # 搜索功能
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
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
    
    @action(detail=False, methods=['post'])
    def bulk_update_order(self, request):
        """批量更新照片排序"""
        if not request.user.is_authenticated:
            return Response({'error': '未授权'}, status=status.HTTP_401_UNAUTHORIZED)
        
        orders = request.data.get('orders', [])
        if not isinstance(orders, list):
            return Response({'error': '无效的数据格式'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            for item in orders:
                photo_id = item.get('id')
                order = item.get('order')
                if photo_id and order is not None:
                    Photo.objects.filter(id=photo_id).update(order=order)
            
            return Response({'success': True, 'message': '排序更新成功'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """批量删除照片"""
        if not request.user.is_authenticated:
            return Response({'error': '未授权'}, status=status.HTTP_401_UNAUTHORIZED)
        
        photo_ids = request.data.get('ids', [])
        if not isinstance(photo_ids, list):
            return Response({'error': '无效的数据格式'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            deleted_count, _ = Photo.objects.filter(id__in=photo_ids).delete()
            return Response({'success': True, 'message': f'成功删除 {deleted_count} 张照片'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

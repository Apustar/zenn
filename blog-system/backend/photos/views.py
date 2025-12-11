from rest_framework import viewsets, permissions
from django.db import models
from .models import Album, Photo
from .serializers import AlbumSerializer, AlbumCreateSerializer, PhotoSerializer


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


class PhotoViewSet(viewsets.ReadOnlyModelViewSet):
    """照片视图集"""
    queryset = Photo.objects.all().select_related('album')
    serializer_class = PhotoSerializer
    permission_classes = [permissions.AllowAny]

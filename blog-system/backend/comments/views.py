from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from .models import Comment, CommentLike
from .serializers import CommentSerializer, CommentCreateSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""
    queryset = Comment.objects.filter(is_approved=True).select_related('author', 'parent')
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # 禁用分页，直接返回数组

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # 根据 content_type 和 object_id 过滤
        content_type_id = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        if content_type_id and object_id:
            queryset = queryset.filter(
                content_type_id=content_type_id,
                object_id=object_id,
                parent__isnull=True  # 只返回顶级评论
            )
        return queryset

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'like']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取关联对象
        content_type_id = request.data.get('content_type')
        object_id = request.data.get('object_id')
        if content_type_id and object_id:
            content_type = ContentType.objects.get_for_id(content_type_id)
            content_object = content_type.get_object_for_this_type(pk=object_id)
            # 将 content_object 传递给 serializer 的 context
            serializer.context['content_object'] = content_object
            serializer.save()
        else:
            serializer.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_context(self):
        """添加 request 到 serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞评论"""
        comment = self.get_object()
        like, created = CommentLike.objects.get_or_create(
            comment=comment,
            user=request.user
        )
        if not created:
            like.delete()
            return Response({'liked': False})
        return Response({'liked': True})

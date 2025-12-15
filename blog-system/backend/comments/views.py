from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from .models import Comment, CommentLike
from .serializers import CommentSerializer, CommentCreateSerializer
from common.email import send_comment_reply_notification, send_new_comment_notification


class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""
    queryset = Comment.objects.filter(is_approved=True).select_related('author', 'parent').order_by('created_at')
    permission_classes = [permissions.AllowAny]
    # 管理员查看所有评论时启用分页，普通用户查询特定内容评论时不分页

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        # 管理员可以查看所有评论（包括未审核的）
        if self.request.user.is_authenticated and self.request.user.is_staff:
            queryset = Comment.objects.all().select_related('author', 'parent').order_by('-created_at')
            
            # 管理员可以按审核状态筛选
            is_approved_param = self.request.query_params.get('is_approved')
            if is_approved_param is not None:
                is_approved = is_approved_param.lower() == 'true'
                queryset = queryset.filter(is_approved=is_approved)
            
            # 管理员可以搜索评论内容
            search = self.request.query_params.get('search')
            if search:
                queryset = queryset.filter(content__icontains=search)
        else:
            queryset = Comment.objects.filter(is_approved=True).select_related('author', 'parent').order_by('created_at')
            
            # 根据 content_type 和 object_id 过滤（非管理员查询）
            content_type_id = self.request.query_params.get('content_type')
            object_id = self.request.query_params.get('object_id')
            if content_type_id and object_id:
                queryset = queryset.filter(
                    content_type_id=content_type_id,
                    object_id=object_id,
                    parent__isnull=True  # 只返回顶级评论
                )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """列表查询，管理员使用分页，普通用户不分页"""
        queryset = self.get_queryset()
        
        # 管理员查看所有评论时使用分页
        if request.user.is_authenticated and request.user.is_staff:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        
        # 普通用户查询特定内容的评论，不分页
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
        content_object = None
        
        if content_type_id and object_id:
            content_type = ContentType.objects.get_for_id(content_type_id)
            content_object = content_type.get_object_for_this_type(pk=object_id)
            # 将 content_object 传递给 serializer 的 context
            serializer.context['content_object'] = content_object
        
        # 保存评论
        comment = serializer.save()
        
        # 发送邮件通知（异步处理，避免阻塞请求）
        try:
            # 如果是回复评论，通知父评论作者
            if comment.parent:
                send_comment_reply_notification(comment, comment.parent)
            
            # 如果是新评论，通知内容作者（文章作者）
            if content_object and not comment.parent:
                send_new_comment_notification(comment, content_object)
        except Exception as e:
            # 邮件发送失败不影响评论创建
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send email notification: {e}", exc_info=True)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_context(self):
        """添加 request 到 serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """审核评论（管理员功能）"""
        comment = self.get_object()
        approved = request.data.get('approved', True)
        comment.is_approved = approved
        comment.save()
        
        # 发送审核通知
        try:
            from common.email import send_comment_approval_notification
            send_comment_approval_notification(comment, approved=approved)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send approval notification: {e}", exc_info=True)
        
        serializer = self.get_serializer(comment)
        return Response(serializer.data)
    
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

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Post, PostLike, PostView
from .serializers import PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer
from .utils import verify_content_password, mark_password_verified_in_session, check_password_verified_in_session


class PostViewSet(viewsets.ModelViewSet):
    """文章视图集"""
    queryset = Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filterset_fields = ['category', 'tags', 'author']
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['created_at', 'published_at', 'views', 'likes']
    ordering = ['-is_top', '-published_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """获取文章详情并记录浏览"""
        instance = self.get_object()
        
        # 记录浏览（避免短时间内重复记录）
        self._record_view(instance, request)
        
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)

    def _record_view(self, post, request):
        """记录文章浏览"""
        # 获取客户端IP地址
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR', '')
        
        # 获取用户代理
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 检查是否在最近1小时内已经浏览过（避免重复记录）
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_view = PostView.objects.filter(
            post=post,
            ip_address=ip_address,
            viewed_at__gte=one_hour_ago
        ).first()
        
        if not recent_view:
            # 创建浏览记录
            PostView.objects.create(
                post=post,
                ip_address=ip_address,
                user_agent=user_agent
            )
            # 更新文章浏览量
            post.views += 1
            post.save(update_fields=['views'])

    def get_queryset(self):
        queryset = super().get_queryset()
        # 管理员可以查看所有文章
        if self.request.user.is_staff:
            queryset = Post.objects.all().select_related('author', 'category').prefetch_related('tags')
        return queryset

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'like']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['post'])
    def like(self, request, slug=None):
        """点赞文章"""
        post = self.get_object()
        like, created = PostLike.objects.get_or_create(
            post=post,
            user=request.user
        )
        if not created:
            like.delete()
            post.likes = max(0, post.likes - 1)
            liked = False
        else:
            post.likes += 1
            liked = True
        post.save(update_fields=['likes'])
        return Response({'liked': liked, 'likes': post.likes})

    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        """获取相关文章"""
        post = self.get_object()
        related_posts = Post.objects.filter(
            Q(category=post.category) | Q(tags__in=post.tags.all()),
            status='published'
        ).exclude(id=post.id).distinct()[:5]
        serializer = PostListSerializer(related_posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def archives(self, request):
        """归档页面"""
        posts = self.get_queryset().order_by('-published_at')
        archives = {}
        for post in posts:
            year = post.published_at.year if post.published_at else post.created_at.year
            month = post.published_at.month if post.published_at else post.created_at.month
            key = f"{year}-{month:02d}"
            if key not in archives:
                archives[key] = []
            archives[key].append(PostListSerializer(post, context={'request': request}).data)
        return Response(archives)
    
    @action(detail=True, methods=['post'])
    def verify_password(self, request, slug=None):
        """验证文章密码"""
        post = self.get_object()
        
        if not post.is_encrypted:
            return Response({'error': '该文章未加密'}, status=status.HTTP_400_BAD_REQUEST)
        
        password = request.data.get('password')
        if not password:
            return Response({'error': '请输入密码'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证密码
        if verify_content_password(post.password, password):
            # 标记为已验证（使用密码更新时间）
            mark_password_verified_in_session(request, 'post', post.id, post.password_updated_at)
            return Response({'success': True, 'message': '密码验证成功'})
        else:
            return Response({'error': '密码错误'}, status=status.HTTP_400_BAD_REQUEST)

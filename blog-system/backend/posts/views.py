from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, F, FloatField, ExpressionWrapper
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from .models import Post, PostLike, PostView
from .serializers import PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer
from .utils import verify_content_password, mark_password_verified_in_session, check_password_verified_in_session
from common.response import api_response, api_error_response


class PostViewSet(viewsets.ModelViewSet):
    """文章视图集"""
    queryset = Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filterset_fields = ['category', 'tags', 'author']
    search_fields = ['title', 'excerpt', 'content']  # SearchFilter 使用，但我们自定义了搜索逻辑
    ordering_fields = ['created_at', 'published_at', 'views', 'likes']
    ordering = ['-is_top', '-published_at']
    
    def get_filter_backends(self):
        """自定义 filter backends，排除 SearchFilter，因为我们自己处理搜索"""
        from rest_framework.filters import OrderingFilter
        from django_filters.rest_framework import DjangoFilterBackend
        return [DjangoFilterBackend, OrderingFilter]
    
    def list(self, request, *args, **kwargs):
        """列表查询，支持搜索和筛选，优化相关度排序"""
        queryset = self.get_queryset()
        
        # 状态筛选（管理员功能）
        status_param = request.query_params.get('status', None)
        if status_param and request.user.is_authenticated and request.user.is_staff:
            queryset = queryset.filter(status=status_param)
        
        # 先应用筛选（分类、标签等）- 手动应用 DjangoFilterBackend
        from django_filters.rest_framework import DjangoFilterBackend
        filter_backend = DjangoFilterBackend()
        queryset = filter_backend.filter_queryset(request, queryset, self)
        
        # 处理自定义搜索
        search = request.query_params.get('search', None)
        if search:
            search = search.strip()
            if search:
                # 使用 Q 对象构建复杂搜索查询
                search_query = Q(title__icontains=search) | Q(excerpt__icontains=search) | Q(content__icontains=search)
                queryset = queryset.filter(search_query)
                
                # 相关度排序：标题匹配 > 摘要匹配 > 内容匹配
                from django.db.models import Case, When, IntegerField
                queryset = queryset.annotate(
                    relevance=Case(
                        When(title__icontains=search, then=3),
                        When(excerpt__icontains=search, then=2),
                        When(content__icontains=search, then=1),
                        default=0,
                        output_field=IntegerField()
                    )
                ).order_by('-relevance', '-published_at', '-created_at')
        else:
            # 如果没有搜索，使用默认排序
            queryset = queryset.order_by('-is_top', '-published_at')
        
        # 应用排序
        from rest_framework.filters import OrderingFilter
        ordering_backend = OrderingFilter()
        queryset = ordering_backend.filter_queryset(request, queryset, self)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
        # 管理员可以查看所有文章（包括草稿）
        # 普通用户可以查看自己创建的文章（包括草稿）和所有已发布的文章
        if self.request.user.is_staff:
            queryset = Post.objects.all().select_related('author', 'category').prefetch_related('tags')
        elif self.request.user.is_authenticated:
            queryset = Post.objects.filter(
                Q(status='published') | Q(author=self.request.user)
            ).select_related('author', 'category').prefetch_related('tags')
        else:
            queryset = Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
        return queryset.order_by('-is_top', '-published_at')

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
        # 优化查询：避免N+1问题，使用prefetch_related
        related_posts = Post.objects.filter(
            Q(category=post.category) | Q(tags__in=post.tags.all()),
            status='published'
        ).exclude(id=post.id).distinct().select_related('author', 'category').prefetch_related('tags')[:5]
        serializer = PostListSerializer(related_posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def archives(self, request):
        """归档页面 - 优化性能"""
        posts = self.get_queryset().order_by('-published_at')
        # 批量序列化以提高性能
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        archives = {}
        for post_data in serializer.data:
            published_at = post_data['published_at'] or post_data['created_at']
            year = int(published_at[:4])
            month = int(published_at[5:7])
            key = f"{year}-{month:02d}"
            if key not in archives:
                archives[key] = []
            archives[key].append(post_data)
        return Response(archives)
    
    @action(detail=True, methods=['post'])
    def verify_password(self, request, slug=None):
        """验证文章密码"""
        post = self.get_object()
        
        if not post.is_encrypted:
            return api_error_response('该文章未加密')
        
        password = request.data.get('password')
        if not password:
            return api_error_response('请输入密码')
        
        # 验证密码
        if verify_content_password(post.password, password):
            # 标记为已验证（使用密码更新时间）
            mark_password_verified_in_session(request, 'post', post.id, post.password_updated_at)
            return api_response({'verified': True}, '密码验证成功')
        else:
            return api_error_response('密码错误')
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def autosave(self, request, slug=None):
        """自动保存文章草稿"""
        try:
            # 获取文章（允许访问草稿）
            queryset = Post.objects.filter(
                Q(status='published') | Q(author=request.user)
            )
            post = queryset.get(slug=slug)
            
            # 检查权限：只有作者可以自动保存
            if post.author != request.user:
                return api_error_response('无权操作此文章', status_code=status.HTTP_403_FORBIDDEN)
            
            # 获取要保存的数据（只更新提供的字段）
            serializer = PostCreateUpdateSerializer(
                post,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            
            if serializer.is_valid():
                # 自动保存时，确保状态为草稿
                saved_post = serializer.save()
                if saved_post.status != 'draft':
                    saved_post.status = 'draft'
                    saved_post.save()
                
                return api_response(
                    {
                        'id': saved_post.id,
                        'slug': saved_post.slug,
                        'title': saved_post.title,
                        'updated_at': saved_post.updated_at.isoformat(),
                    },
                    '自动保存成功'
                )
            else:
                return api_error_response('数据验证失败', errors=serializer.errors)
                
        except Post.DoesNotExist:
            return api_error_response('文章不存在', status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_error_response(f'自动保存失败：{str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def autosave_create(self, request):
        """为新文章自动保存（创建草稿）"""
        try:
            # 创建新草稿
            serializer = PostCreateUpdateSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                # 确保状态为草稿
                post_data = serializer.validated_data
                post_data['status'] = 'draft'
                post_data['author'] = request.user
                
                saved_post = serializer.save()
                
                return api_response(
                    {
                        'id': saved_post.id,
                        'slug': saved_post.slug,
                        'title': saved_post.title,
                        'updated_at': saved_post.updated_at.isoformat(),
                    },
                    '草稿创建成功'
                )
            else:
                return api_error_response('数据验证失败', errors=serializer.errors)
                
        except Exception as e:
            return api_error_response(f'创建草稿失败：{str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def hot(self, request):
        """获取热门文章（基于浏览量、点赞数、评论数、时间衰减的综合评分）"""
        try:
            from comments.models import Comment
            
            # 获取 ContentType for Post
            post_content_type = ContentType.objects.get_for_model(Post)
            
            # 计算时间衰减因子（文章发布后的天数）
            now = timezone.now()
            
            # 获取已发布的文章
            posts_list = list(Post.objects.filter(
                status='published',
                is_encrypted=False  # 排除加密文章
            ).select_related('author', 'category').prefetch_related('tags'))
            
            if not posts_list:
                return Response([])
            
            # 批量获取评论数
            post_ids = [p.id for p in posts_list]
            comment_counts = Comment.objects.filter(
                content_type=post_content_type,
                object_id__in=post_ids,
                is_approved=True
            ).values('object_id').annotate(count=Count('id'))
            
            comment_count_dict = {item['object_id']: item['count'] for item in comment_counts}
            
            # 为每篇文章计算热门度评分
            scored_posts = []
            for post in posts_list:
                comment_count = comment_count_dict.get(post.id, 0)
                
                # 计算发布后的天数
                if post.published_at:
                    days = (now - post.published_at).total_seconds() / 86400  # 转换为天数
                else:
                    days = (now - post.created_at).total_seconds() / 86400
                
                # 热门度评分公式：score = (views * 0.3 + likes * 0.4 + comment_count * 0.3) / (days + 1)^0.5
                # 时间衰减：越新的文章权重越高
                hot_score = (
                    post.views * 0.3 +
                    post.likes * 0.4 +
                    comment_count * 0.3
                ) / ((days + 1) ** 0.5)
                
                scored_posts.append((post, hot_score))
            
            # 按热门度排序
            scored_posts.sort(key=lambda x: x[1], reverse=True)
            
            # 取前10篇
            hot_posts = [post for post, _ in scored_posts[:10]]
            
            serializer = PostListSerializer(hot_posts, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return api_error_response(f'获取热门文章失败：{str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def search_suggestions(self, request):
        """获取搜索建议（基于标题和摘要）"""
        try:
            keyword = request.query_params.get('q', '').strip()
            if not keyword or len(keyword) < 2:
                return Response([])
            
            # 搜索标题和摘要中包含关键词的文章
            suggestions = Post.objects.filter(
                status='published',
                is_encrypted=False
            ).filter(
                Q(title__icontains=keyword) | Q(excerpt__icontains=keyword)
            ).values_list('title', flat=True).distinct()[:5]
            
            return Response(list(suggestions))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'获取搜索建议失败：{str(e)}', exc_info=True)
            return Response([])  # 失败时返回空数组，不抛出错误
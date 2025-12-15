from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SiteSettings, NavigationItem
from .serializers import (
    SiteSettingsSerializer, SiteSettingsUpdateSerializer,
    NavigationItemSerializer, NavigationItemCreateUpdateSerializer
)
from common.email import send_email_notification


class SiteSettingsViewSet(viewsets.ModelViewSet):
    """站点设置视图集"""
    queryset = SiteSettings.objects.all()
    permission_classes = [permissions.AllowAny]  # 获取设置允许任何人访问
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return SiteSettingsUpdateSerializer
        return SiteSettingsSerializer

    def get_permissions(self):
        """更新设置需要管理员权限"""
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_serializer_context(self):
        """添加 request 到 serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request):
        """获取站点设置（单例）"""
        settings = SiteSettings.get_settings()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """获取站点设置"""
        settings = SiteSettings.get_settings()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """更新站点设置"""
        settings = SiteSettings.get_settings()
        serializer = SiteSettingsUpdateSerializer(settings, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(SiteSettingsSerializer(settings, context={'request': request}).data)

    def partial_update(self, request, pk=None):
        """部分更新站点设置"""
        return self.update(request, pk)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def test_email(self, request):
        """测试邮件发送功能"""
        test_email = request.data.get('email', request.user.email)
        
        if not test_email:
            return Response(
                {'error': '请提供测试邮箱地址'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        site_settings = SiteSettings.get_settings()
        subject = f"【{site_settings.site_name}】邮件测试"
        message = f"""
您好，

这是一封来自 {site_settings.site_name} 的测试邮件。

如果您收到这封邮件，说明邮件配置正确，邮件通知功能已正常工作。

---
{site_settings.site_name}
"""
        # 使用模板生成 HTML 内容
        from django.template.loader import render_to_string
        context = {
            'site_name': site_settings.site_name,
        }
        html_message = render_to_string('common/email/test.html', context)
        
        try:
            success = send_email_notification(
                subject=subject,
                message=message.strip(),
                recipient_list=[test_email],
                html_message=html_message,
                notification_type='test',
                async_send=False,  # 测试邮件同步发送，立即返回结果
            )
            
            if success:
                return Response({
                    'success': True,
                    'message': f'测试邮件已发送到 {test_email}，请查收。'
                })
            else:
                return Response(
                    {
                        'success': False,
                        'message': '邮件发送失败，请检查邮件配置是否正确。'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f'邮件发送失败：{str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NavigationItemViewSet(viewsets.ModelViewSet):
    """导航菜单视图集"""
    queryset = NavigationItem.objects.all()
    permission_classes = [permissions.AllowAny]  # 获取菜单允许任何人访问
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NavigationItemCreateUpdateSerializer
        return NavigationItemSerializer

    def get_permissions(self):
        """更新菜单需要管理员权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        """获取可见的导航菜单"""
        # 如果数据库中没有菜单，先初始化
        if not NavigationItem.objects.exists():
            NavigationItem.initialize_builtin_items()
        
        queryset = super().get_queryset()
        # 对于 list 和 retrieve 操作（前端获取），始终只返回可见的菜单
        # 管理员在 Admin 界面可以查看所有菜单项
        if self.action in ['list', 'retrieve', None]:
            queryset = queryset.filter(is_visible=True)
        return queryset

    def list(self, request, *args, **kwargs):
        """重写 list 方法，管理员可以查看所有菜单项，普通用户只能看到可见的"""
        # 如果数据库中没有菜单，先初始化
        if not NavigationItem.objects.exists():
            NavigationItem.initialize_builtin_items()
        
        # 管理员可以查看所有菜单项（包括隐藏的）
        if request.user.is_authenticated and request.user.is_staff:
            queryset = NavigationItem.objects.all().order_by('order', 'id')
        else:
            # 普通用户只获取可见的菜单项
            queryset = NavigationItem.objects.filter(is_visible=True).order_by('order', 'id')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """删除菜单项（系统内置不可删除）"""
        instance = self.get_object()
        if instance.is_builtin:
            return Response(
                {'error': '系统内置菜单不可删除'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def initialize(self, request):
        """初始化系统内置菜单（管理员）"""
        NavigationItem.initialize_builtin_items()
        return Response({'message': '内置菜单已初始化'})
    
    @action(detail=False, methods=['get'])
    def check_access(self, request):
        """检查URL是否可以访问"""
        url_path = request.query_params.get('url', '')
        if not url_path:
            return Response({'accessible': False, 'error': 'URL参数缺失'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 标准化URL路径
        normalized_path = url_path.rstrip('/') or '/'
        is_accessible = NavigationItem.check_url_access(normalized_path)
        
        return Response({
            'url': normalized_path,
            'accessible': is_accessible
        })

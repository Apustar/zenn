from django.db import models


class SiteSettings(models.Model):
    """站点设置模型（单例模式）"""
    site_name = models.CharField(max_length=100, default='我的博客', verbose_name='博客名称')
    site_description = models.TextField(max_length=500, blank=True, verbose_name='博客描述')
    site_keywords = models.CharField(max_length=200, blank=True, verbose_name='关键词')
    site_icon = models.ImageField(
        upload_to='settings/',
        null=True,
        blank=True,
        verbose_name='站点图标',
        help_text='支持 PNG、JPG、SVG 等格式，建议尺寸 24x24 像素'
    )
    about_content = models.TextField(blank=True, verbose_name='关于页面内容', help_text='支持 Markdown 格式')
    
    # 邮件通知配置
    enable_email_notification = models.BooleanField(default=False, verbose_name='启用邮件通知', help_text='是否启用邮件通知功能')
    email_host = models.CharField(max_length=200, blank=True, verbose_name='SMTP 服务器', help_text='例如：smtp.gmail.com')
    email_port = models.IntegerField(default=587, verbose_name='SMTP 端口', help_text='常用端口：587 (TLS) 或 465 (SSL)')
    email_use_tls = models.BooleanField(default=True, verbose_name='使用 TLS', help_text='是否使用 TLS 加密')
    email_use_ssl = models.BooleanField(default=False, verbose_name='使用 SSL', help_text='是否使用 SSL 加密')
    email_host_user = models.CharField(max_length=200, blank=True, verbose_name='SMTP 用户名', help_text='发送邮件的邮箱地址')
    email_host_password = models.CharField(max_length=200, blank=True, verbose_name='SMTP 密码', help_text='邮箱密码或应用专用密码')
    email_from = models.CharField(max_length=200, blank=True, verbose_name='发件人邮箱', help_text='显示的发件人邮箱地址')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '站点设置'
        verbose_name_plural = '站点设置'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        """确保只有一个实例"""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """获取站点设置（单例）"""
        settings, created = cls.objects.get_or_create(pk=1, defaults={'site_name': '我的博客'})
        return settings


class NavigationItem(models.Model):
    """导航菜单项模型"""
    name = models.CharField(max_length=50, verbose_name='菜单名称')
    url = models.CharField(max_length=200, verbose_name='链接地址')
    is_builtin = models.BooleanField(default=False, verbose_name='系统内置', help_text='系统内置菜单不可删除')
    is_visible = models.BooleanField(default=True, verbose_name='是否显示', help_text='控制是否在导航栏显示')
    is_accessible = models.BooleanField(default=True, verbose_name='是否可访问', help_text='控制是否可以通过URL访问，设为False时访问会显示404')
    order = models.IntegerField(default=0, verbose_name='排序', help_text='数字越小越靠前')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '导航菜单'
        verbose_name_plural = '导航菜单'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

    @classmethod
    def initialize_builtin_items(cls):
        """初始化系统内置菜单项"""
        builtin_items = [
            {'name': '首页', 'url': '/', 'is_builtin': True, 'is_visible': True, 'is_accessible': True, 'order': 0},
            {'name': '瞬间', 'url': '/moments', 'is_builtin': True, 'is_visible': True, 'is_accessible': True, 'order': 1},
            {'name': '相册', 'url': '/photos', 'is_builtin': True, 'is_visible': True, 'is_accessible': True, 'order': 2},
            {'name': '友链', 'url': '/links', 'is_builtin': True, 'is_visible': True, 'is_accessible': True, 'order': 3},
            {'name': '归档', 'url': '/archives', 'is_builtin': True, 'is_visible': True, 'is_accessible': True, 'order': 4},
            {'name': '关于', 'url': '/about', 'is_builtin': True, 'is_visible': True, 'is_accessible': True, 'order': 5},
        ]
        
        for item_data in builtin_items:
            cls.objects.get_or_create(
                url=item_data['url'],
                defaults=item_data
            )
    
    @classmethod
    def check_url_access(cls, url_path):
        """检查URL是否可以访问"""
        try:
            # 标准化URL路径（移除末尾的斜杠）
            normalized_path = url_path.rstrip('/') or '/'
            item = cls.objects.filter(url=normalized_path).first()
            if item:
                return item.is_accessible
            # 如果没有找到对应的菜单项，默认允许访问（兼容其他路由）
            return True
        except Exception:
            return True

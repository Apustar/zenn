from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import markdown
import bleach
from .utils import hash_content_password

User = get_user_model()


class Post(models.Model):
    """文章模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]

    title = models.CharField(max_length=200, verbose_name='标题')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL 别名')
    excerpt = models.TextField(max_length=500, blank=True, verbose_name='摘要')
    content = models.TextField(verbose_name='内容')
    content_html = models.TextField(editable=False, verbose_name='HTML 内容')
    cover = models.ImageField(upload_to='posts/', null=True, blank=True, verbose_name='封面图')
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='作者')
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='分类'
    )
    tags = models.ManyToManyField('tags.Tag', blank=True, related_name='posts', verbose_name='标签')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    is_top = models.BooleanField(default=False, verbose_name='置顶')
    is_original = models.BooleanField(default=True, verbose_name='原创')
    allow_comment = models.BooleanField(default=True, verbose_name='允许评论')
    is_encrypted = models.BooleanField(default=False, verbose_name='是否加密')
    password = models.CharField(max_length=128, blank=True, verbose_name='访问密码', help_text='加密文章的访问密码')
    password_updated_at = models.DateTimeField(null=True, blank=True, verbose_name='密码更新时间', help_text='用于检测密码是否被修改')
    
    views = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    likes = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-is_top', '-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # 处理加密密码
        password_changed = False
        
        # 获取旧的密码（如果存在）
        old_password = None
        if self.pk:
            try:
                old_instance = Post.objects.get(pk=self.pk)
                old_password = old_instance.password
            except Post.DoesNotExist:
                pass
        
        if self.is_encrypted and self.password:
            # 如果密码不是以pbkdf2_sha256开头（Django密码格式），说明是明文，需要哈希
            if not self.password.startswith('pbkdf2_sha256$'):
                new_password_hash = hash_content_password(self.password)
                # 检查密码是否真的改变了
                if old_password != new_password_hash:
                    password_changed = True
                self.password = new_password_hash
            else:
                # 已经是哈希格式，直接比较
                if old_password != self.password:
                    password_changed = True
        elif not self.is_encrypted:
            # 如果不加密，清空密码
            if old_password and old_password != '':
                password_changed = True
            self.password = ''
        
        # 如果密码被修改，更新 password_updated_at
        if password_changed:
            from django.utils import timezone
            self.password_updated_at = timezone.now()
        # 将 Markdown 转换为 HTML
        if self.content:
            html = markdown.markdown(
                self.content,
                extensions=['codehilite', 'fenced_code', 'tables', 'toc']
            )
            # 清理 HTML，防止 XSS
            allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'code', 'table', 'thead', 'tbody', 'tr', 'th', 'td']
            self.content_html = bleach.clean(
                html,
                tags=allowed_tags,
                attributes=bleach.sanitizer.ALLOWED_ATTRIBUTES
            )
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'slug': self.slug})

    def get_word_count(self):
        """获取文章字数"""
        return len(self.content)

    def get_read_time(self):
        """估算阅读时间（分钟）"""
        word_count = self.get_word_count()
        # 假设每分钟阅读 200 字
        return max(1, round(word_count / 200))


class PostLike(models.Model):
    """文章点赞"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']
        verbose_name = '文章点赞'
        verbose_name_plural = '文章点赞'


class PostView(models.Model):
    """文章浏览记录"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='view_records')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '浏览记录'
        verbose_name_plural = '浏览记录'
        ordering = ['-viewed_at']

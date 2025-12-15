from django.db import models
from django.contrib.auth import get_user_model
from .utils import hash_content_password

User = get_user_model()


class Album(models.Model):
    """相册模型"""
    name = models.CharField(max_length=100, verbose_name='相册名称')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL 别名')
    description = models.TextField(blank=True, verbose_name='描述')
    cover = models.ImageField(upload_to='albums/', null=True, blank=True, verbose_name='封面图')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums', verbose_name='作者')
    order = models.IntegerField(default=0, verbose_name='排序')
    is_encrypted = models.BooleanField(default=False, verbose_name='是否加密')
    password = models.CharField(max_length=128, blank=True, verbose_name='访问密码', help_text='加密相册的访问密码')
    password_updated_at = models.DateTimeField(null=True, blank=True, verbose_name='密码更新时间', help_text='用于检测密码是否被修改')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '相册'
        verbose_name_plural = '相册'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # 处理加密密码
        self._handle_password()
        
        super().save(*args, **kwargs)
    
    def _handle_password(self):
        """处理相册密码加密和更新时间"""
        password_changed = False
        old_password = None
        
        # 获取旧的密码（如果存在）
        if self.pk:
            try:
                old_instance = Album.objects.get(pk=self.pk)
                old_password = old_instance.password
            except Album.DoesNotExist:
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


class Photo(models.Model):
    """照片模型"""
    title = models.CharField(max_length=200, blank=True, verbose_name='标题')
    image = models.ImageField(upload_to='photos/', verbose_name='图片')
    description = models.TextField(blank=True, verbose_name='描述')
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='相册'
    )
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '照片'
        verbose_name_plural = '照片'
        ordering = ['album', 'order', '-created_at']

    def __str__(self):
        return self.title or f'Photo {self.id}'

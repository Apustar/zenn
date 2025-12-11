from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Album(models.Model):
    """相册模型"""
    name = models.CharField(max_length=100, verbose_name='相册名称')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL 别名')
    description = models.TextField(blank=True, verbose_name='描述')
    cover = models.ImageField(upload_to='albums/', null=True, blank=True, verbose_name='封面图')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums', verbose_name='作者')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '相册'
        verbose_name_plural = '相册'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name


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

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Moment(models.Model):
    """瞬间（说说）模型"""
    VISIBILITY_CHOICES = [
        ('public', '公开'),
        ('private', '私密'),
    ]

    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moments', verbose_name='作者')
    
    images = models.JSONField(default=list, blank=True, verbose_name='图片列表')
    location = models.CharField(max_length=200, blank=True, verbose_name='位置')
    
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public', verbose_name='可见性')
    
    likes = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    comments_count = models.PositiveIntegerField(default=0, verbose_name='评论数')
    
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '瞬间'
        verbose_name_plural = '瞬间'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['author', '-published_at']),
        ]

    def __str__(self):
        return f'{self.author.username} 的瞬间: {self.content[:50]}'


class MomentLike(models.Model):
    """瞬间点赞"""
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, related_name='like_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moment_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['moment', 'user']
        verbose_name = '瞬间点赞'
        verbose_name_plural = '瞬间点赞'

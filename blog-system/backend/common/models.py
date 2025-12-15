"""
通用模型
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailLog(models.Model):
    """邮件发送日志"""
    STATUS_CHOICES = [
        ('pending', '待发送'),
        ('success', '发送成功'),
        ('failed', '发送失败'),
    ]
    
    recipient = models.EmailField(verbose_name='收件人')
    subject = models.CharField(max_length=200, verbose_name='邮件主题')
    message = models.TextField(verbose_name='邮件内容')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='发送状态')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    notification_type = models.CharField(max_length=50, blank=True, verbose_name='通知类型', help_text='例如：comment_reply, new_comment, comment_approval')
    related_object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='关联对象ID')
    related_object_type = models.CharField(max_length=100, blank=True, verbose_name='关联对象类型')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='发送时间')
    
    class Meta:
        verbose_name = '邮件日志'
        verbose_name_plural = '邮件日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['recipient', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient} - {self.subject} ({self.status})"


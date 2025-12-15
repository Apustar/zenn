"""
通用管理界面
"""
from django.contrib import admin
from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """邮件日志管理"""
    list_display = ['recipient', 'subject', 'status', 'notification_type', 'created_at', 'sent_at']
    list_filter = ['status', 'notification_type', 'created_at']
    search_fields = ['recipient', 'subject', 'message']
    readonly_fields = ['created_at', 'sent_at', 'related_object_id', 'related_object_type']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('recipient', 'subject', 'message', 'status')
        }),
        ('详细信息', {
            'fields': ('notification_type', 'related_object_type', 'related_object_id', 'error_message')
        }),
        ('时间信息', {
            'fields': ('created_at', 'sent_at')
        }),
    )
    
    def has_add_permission(self, request):
        """禁止手动添加邮件日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """只允许查看，不允许修改"""
        return False


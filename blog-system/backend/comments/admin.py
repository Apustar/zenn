from django.contrib import admin
from django.db.models import Q
from .models import Comment, CommentLike
from common.email import send_comment_approval_notification


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['content_object', 'author', 'parent', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username']
    readonly_fields = ['ip_address', 'user_agent', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_editable = ['is_approved']
    actions = ['approve_comments', 'reject_comments']
    
    def save_model(self, request, obj, form, change):
        """保存评论时，如果审核状态改变，发送通知"""
        if change:
            # 获取旧的审核状态
            old_obj = Comment.objects.get(pk=obj.pk)
            old_approved = old_obj.is_approved
            new_approved = obj.is_approved
            
            # 如果审核状态改变，发送通知
            if old_approved != new_approved:
                super().save_model(request, obj, form, change)
                try:
                    send_comment_approval_notification(obj, approved=new_approved)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to send approval notification: {e}", exc_info=True)
            else:
                super().save_model(request, obj, form, change)
        else:
            super().save_model(request, obj, form, change)
    
    @admin.action(description='批量通过审核')
    def approve_comments(self, request, queryset):
        """批量通过审核"""
        updated = queryset.update(is_approved=True)
        # 发送通知
        for comment in queryset:
            try:
                send_comment_approval_notification(comment, approved=True)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send approval notification: {e}", exc_info=True)
        self.message_user(request, f'已通过 {updated} 条评论的审核')
    
    @admin.action(description='批量拒绝审核')
    def reject_comments(self, request, queryset):
        """批量拒绝审核"""
        updated = queryset.update(is_approved=False)
        # 发送通知
        for comment in queryset:
            try:
                send_comment_approval_notification(comment, approved=False)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send rejection notification: {e}", exc_info=True)
        self.message_user(request, f'已拒绝 {updated} 条评论的审核')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['comment', 'user', 'created_at']
    list_filter = ['created_at']

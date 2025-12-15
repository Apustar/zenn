"""
邮件发送工具函数
"""
import logging
import threading
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from settings.models import SiteSettings
from .models import EmailLog

logger = logging.getLogger(__name__)


def get_email_config():
    """获取邮件配置（从站点设置或 Django settings）"""
    try:
        site_settings = SiteSettings.get_settings()
        if site_settings.enable_email_notification and site_settings.email_host:
            return {
                'enabled': True,
                'host': site_settings.email_host,
                'port': site_settings.email_port,
                'use_tls': site_settings.email_use_tls,
                'use_ssl': site_settings.email_use_ssl,
                'host_user': site_settings.email_host_user,
                'host_password': site_settings.email_host_password,
                'from_email': site_settings.email_from or site_settings.email_host_user,
            }
    except Exception as e:
        logger.warning(f"Failed to get email config from site settings: {e}")
    
    # 如果没有配置，尝试从 Django settings 获取
    return {
        'enabled': getattr(settings, 'EMAIL_HOST', None) is not None,
        'host': getattr(settings, 'EMAIL_HOST', ''),
        'port': getattr(settings, 'EMAIL_PORT', 587),
        'use_tls': getattr(settings, 'EMAIL_USE_TLS', True),
        'use_ssl': getattr(settings, 'EMAIL_USE_SSL', False),
        'host_user': getattr(settings, 'EMAIL_HOST_USER', ''),
        'host_password': getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
        'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', getattr(settings, 'EMAIL_HOST_USER', '')),
    }


def apply_email_config(email_config):
    """
    动态应用邮件配置到 Django settings
    注意：这不会修改 settings 模块，而是返回一个配置好的连接对象
    """
    if not email_config['enabled']:
        return None
    
    try:
        connection = get_connection(
            host=email_config['host'],
            port=email_config['port'],
            username=email_config['host_user'],
            password=email_config['host_password'],
            use_tls=email_config['use_tls'],
            use_ssl=email_config['use_ssl'],
            fail_silently=False,
        )
        return connection
    except Exception as e:
        logger.error(f"Failed to create email connection: {e}", exc_info=True)
        return None


def send_email_notification(subject, message, recipient_list, html_message=None, 
                            notification_type='', related_object=None, async_send=True):
    """
    发送邮件通知
    
    Args:
        subject: 邮件主题
        message: 纯文本邮件内容
        recipient_list: 收件人列表
        html_message: HTML 格式的邮件内容（可选）
        notification_type: 通知类型（用于日志记录）
        related_object: 关联对象（用于日志记录）
        async_send: 是否异步发送（默认 True）
    
    Returns:
        bool: 是否发送成功（异步发送时立即返回 True）
    """
    if not recipient_list:
        return False
    
    # 过滤掉无效的邮箱地址
    recipient_list = [email for email in recipient_list if email and '@' in email]
    if not recipient_list:
        return False
    
    email_config = get_email_config()
    
    # 检查是否启用邮件通知
    if not email_config['enabled']:
        logger.info("Email notification is disabled")
        return False
    
    # 记录邮件日志
    email_logs = []
    for recipient in recipient_list:
        log = EmailLog.objects.create(
            recipient=recipient,
            subject=subject,
            message=message[:500],  # 只保存前500字符
            status='pending',
            notification_type=notification_type,
            related_object_id=related_object.pk if related_object else None,
            related_object_type=related_object.__class__.__name__ if related_object else '',
        )
        email_logs.append(log)
    
    # 异步发送邮件
    if async_send:
        thread = threading.Thread(
            target=_send_email_sync,
            args=(subject, message, recipient_list, html_message, email_config, email_logs)
        )
        thread.daemon = True
        thread.start()
        return True
    else:
        return _send_email_sync(subject, message, recipient_list, html_message, email_config, email_logs)


def _send_email_sync(subject, message, recipient_list, html_message, email_config, email_logs):
    """
    同步发送邮件的内部函数
    """
    try:
        # 创建邮件连接
        connection = apply_email_config(email_config)
        
        if html_message:
            # 发送 HTML 邮件
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=email_config['from_email'],
                to=recipient_list,
                connection=connection,
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
        else:
            # 发送纯文本邮件
            send_mail(
                subject=subject,
                message=message,
                from_email=email_config['from_email'],
                recipient_list=recipient_list,
                fail_silently=False,
                connection=connection,
            )
        
        # 更新日志状态
        sent_at = timezone.now()
        for log in email_logs:
            log.status = 'success'
            log.sent_at = sent_at
            log.save()
        
        logger.info(f"Email sent successfully to {recipient_list}")
        return True
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send email: {error_msg}", exc_info=True)
        
        # 更新日志状态
        for log in email_logs:
            log.status = 'failed'
            log.error_message = error_msg[:500]  # 只保存前500字符
            log.save()
        
        return False


def send_comment_reply_notification(reply_comment, parent_comment):
    """
    发送评论回复通知
    
    Args:
        reply_comment: 回复的评论对象
        parent_comment: 被回复的父评论对象
    """
    # 如果回复的是自己，不发送通知
    if reply_comment.author == parent_comment.author:
        return
    
    # 如果父评论作者没有邮箱，不发送
    if not parent_comment.author.email:
        return
    
    try:
        site_settings = SiteSettings.get_settings()
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        
        # 获取关联对象（文章）的标题和链接
        content_title = "文章"
        content_url = frontend_url
        if hasattr(reply_comment.content_object, 'title'):
            content_title = reply_comment.content_object.title
            if hasattr(reply_comment.content_object, 'slug'):
                content_url = f"{frontend_url}/post/{reply_comment.content_object.slug}"
        
        subject = f"【{site_settings.site_name}】有人回复了您的评论"
        
        # 准备模板上下文
        context = {
            'site_name': site_settings.site_name,
            'parent_author': parent_comment.author.username,
            'reply_author': reply_comment.author.username,
            'reply_content': reply_comment.content,
            'parent_content': parent_comment.content[:200] + ('...' if len(parent_comment.content) > 200 else ''),
            'content_title': content_title,
            'content_url': content_url,
            'reply_url': f"{content_url}#comment-{reply_comment.id}",
        }
        
        # 使用模板生成 HTML 内容
        html_message = render_to_string('common/email/comment_reply.html', context)
        
        # 纯文本内容（简化版）
        message = f"""
您好 {parent_comment.author.username}，

{reply_comment.author.username} 回复了您在《{content_title}》下的评论：

您的评论：
{parent_comment.content[:200]}{'...' if len(parent_comment.content) > 200 else ''}

{reply_comment.author.username} 的回复：
{reply_comment.content}

查看完整内容：{content_url}#comment-{reply_comment.id}

---
{site_settings.site_name}
"""
        
        send_email_notification(
            subject=subject,
            message=message.strip(),
            recipient_list=[parent_comment.author.email],
            html_message=html_message,
            notification_type='comment_reply',
            related_object=reply_comment,
        )
    except Exception as e:
        logger.error(f"Failed to send comment reply notification: {e}", exc_info=True)


def send_new_comment_notification(comment, content_object):
    """
    发送新评论通知（通知文章作者）
    
    Args:
        comment: 新评论对象
        content_object: 关联的内容对象（如文章）
    """
    # 如果评论者是内容作者，不发送通知
    if hasattr(content_object, 'author') and comment.author == content_object.author:
        return
    
    # 如果内容作者没有邮箱，不发送
    if not hasattr(content_object, 'author') or not content_object.author.email:
        return
    
    try:
        site_settings = SiteSettings.get_settings()
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        
        # 获取内容标题和链接
        content_title = "内容"
        content_url = frontend_url
        if hasattr(content_object, 'title'):
            content_title = content_object.title
            if hasattr(content_object, 'slug'):
                content_url = f"{frontend_url}/post/{content_object.slug}"
        
        subject = f"【{site_settings.site_name}】您的文章收到了新评论"
        
        # 准备模板上下文
        context = {
            'site_name': site_settings.site_name,
            'author': content_object.author.username,
            'comment_author': comment.author.username,
            'comment_content': comment.content,
            'content_title': content_title,
            'content_url': content_url,
            'comment_url': f"{content_url}#comment-{comment.id}",
        }
        
        # 使用模板生成 HTML 内容
        html_message = render_to_string('common/email/new_comment.html', context)
        
        # 纯文本内容
        message = f"""
您好 {content_object.author.username}，

您的文章《{content_title}》收到了来自 {comment.author.username} 的新评论：

{comment.content}

查看完整内容：{content_url}#comment-{comment.id}

---
{site_settings.site_name}
"""
        
        send_email_notification(
            subject=subject,
            message=message.strip(),
            recipient_list=[content_object.author.email],
            html_message=html_message,
            notification_type='new_comment',
            related_object=comment,
        )
    except Exception as e:
        logger.error(f"Failed to send new comment notification: {e}", exc_info=True)


def send_comment_approval_notification(comment, approved=True):
    """
    发送评论审核通知
    
    Args:
        comment: 评论对象
        approved: 是否通过审核（True=通过，False=拒绝）
    """
    # 如果评论者没有邮箱，不发送
    if not comment.author.email:
        return
    
    try:
        site_settings = SiteSettings.get_settings()
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        
        # 获取关联对象信息
        content_title = "文章"
        content_url = frontend_url
        if hasattr(comment.content_object, 'title'):
            content_title = comment.content_object.title
            if hasattr(comment.content_object, 'slug'):
                content_url = f"{frontend_url}/post/{comment.content_object.slug}"
        
        if approved:
            subject = f"【{site_settings.site_name}】您的评论已通过审核"
            status_text = "已通过审核"
            status_class = "success"
        else:
            subject = f"【{site_settings.site_name}】您的评论未通过审核"
            status_text = "未通过审核"
            status_class = "failed"
        
        # 准备模板上下文
        context = {
            'site_name': site_settings.site_name,
            'author': comment.author.username,
            'status_text': status_text,
            'status_class': status_class,
            'comment_content': comment.content,
            'content_title': content_title,
            'content_url': content_url,
        }
        
        # 使用模板生成 HTML 内容
        html_message = render_to_string('common/email/comment_approval.html', context)
        
        # 纯文本内容
        message = f"""
您好 {comment.author.username}，

您在《{content_title}》下的评论{status_text}。

您的评论：
{comment.content}

查看文章：{content_url}

---
{site_settings.site_name}
"""
        
        send_email_notification(
            subject=subject,
            message=message.strip(),
            recipient_list=[comment.author.email],
            html_message=html_message,
            notification_type='comment_approval',
            related_object=comment,
        )
    except Exception as e:
        logger.error(f"Failed to send comment approval notification: {e}", exc_info=True)


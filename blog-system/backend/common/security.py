"""
安全相关工具函数
"""
import re
import bleach
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import escape


def sanitize_html(content: str, allowed_tags: list = None, allowed_attributes: dict = None) -> str:
    """
    清理HTML内容，防止XSS攻击
    
    Args:
        content: 待清理的HTML内容
        allowed_tags: 允许的HTML标签列表
        allowed_attributes: 允许的属性字典
    
    Returns:
        清理后的HTML内容
    """
    if not content:
        return ''
    
    # 默认允许的标签和属性
    default_tags = [
        'p', 'br', 'strong', 'em', 'u', 'i', 'b', 'span', 'div',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'pre', 'code',
        'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ]
    
    default_attributes = {
        '*': ['class'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'blockquote': ['cite'],
        'code': ['class'],
        'pre': ['class']
    }
    
    tags = allowed_tags or default_tags
    attributes = allowed_attributes or default_attributes
    
    # 使用bleach清理HTML
    cleaned = bleach.clean(
        content,
        tags=tags,
        attributes=attributes,
        strip=True
    )
    
    return cleaned


def validate_password_strength(password: str) -> bool:
    """
    验证密码强度
    
    Args:
        password: 待验证的密码
    
    Returns:
        bool: 密码是否符合强度要求
    """
    if not password:
        return False
    
    # 密码长度至少8位
    if len(password) < 8:
        return False
    
    # 包含至少一个数字
    if not re.search(r'\d', password):
        return False
    
    # 包含至少一个字母
    if not re.search(r'[a-zA-Z]', password):
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，防止路径遍历攻击
    
    Args:
        filename: 原始文件名
    
    Returns:
        str: 清理后的文件名
    """
    if not filename:
        return ''
    
    # 移除路径分隔符和其他危险字符
    filename = re.sub(r'[\\/:"*?<>|]', '', filename)
    
    # 移除开头的点（隐藏文件）
    filename = filename.lstrip('.')
    
    # 限制文件名长度
    max_length = 255
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:max_length - len(ext) - 1] + '.' + ext if ext else name[:max_length]
    
    return filename


def validate_url(url: str) -> bool:
    """
    验证URL是否安全
    
    Args:
        url: 待验证的URL
    
    Returns:
        bool: URL是否安全
    """
    if not url:
        return False
    
    # 基本URL格式验证
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None


def escape_user_input(content: str) -> str:
    """
    转义用户输入，防止XSS
    
    Args:
        content: 用户输入内容
    
    Returns:
        str: 转义后的内容
    """
    if not content:
        return ''
    
    return escape(content)


def rate_limit_key(identifier: str, action: str) -> str:
    """
    生成限流键
    
    Args:
        identifier: 标识符（如IP地址、用户ID）
        action: 操作类型
    
    Returns:
        str: 限流键
    """
    return f"rate_limit:{action}:{identifier}"


def is_safe_redirect_url(url: str, allowed_hosts: list = None) -> bool:
    """
    检查重定向URL是否安全
    
    Args:
        url: 重定向URL
        allowed_hosts: 允许的主机列表
    
    Returns:
        bool: URL是否安全
    """
    if not url:
        return False
    
    # 检查是否是相对URL
    if url.startswith('/') and not url.startswith('//'):
        return True
    
    # 检查是否在允许的主机列表中
    hosts = allowed_hosts or getattr(settings, 'ALLOWED_HOSTS', [])
    for host in hosts:
        if url.startswith(f'http://{host}/') or url.startswith(f'https://{host}/'):
            return True
    
    return False


class SecurityValidator:
    """安全验证器类"""
    
    @staticmethod
    def validate_comment_content(content: str) -> str:
        """验证并清理评论内容"""
        if not content or not content.strip():
            raise ValidationError('评论内容不能为空')
        
        if len(content) > 1000:
            raise ValidationError('评论内容不能超过1000字符')
        
        # 清理HTML标签，只允许纯文本
        return escape_user_input(content)
    
    @staticmethod
    def validate_post_content(content: str) -> str:
        """验证并清理文章内容"""
        if not content or not content.strip():
            raise ValidationError('文章内容不能为空')
        
        # 允许的HTML标签
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'i', 'b',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'blockquote', 'pre', 'code',
            'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
        ]
        
        return sanitize_html(content, allowed_tags)
    
    @staticmethod
    def validate_user_bio(bio: str) -> str:
        """验证并清理用户简介"""
        if not bio:
            return ''
        
        if len(bio) > 500:
            raise ValidationError('个人简介不能超过500字符')
        
        # 只允许纯文本
        return escape_user_input(bio)

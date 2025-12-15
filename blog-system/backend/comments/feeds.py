"""
评论 RSS Feed 定义
"""
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from django.contrib.contenttypes.models import ContentType
from .models import Comment
from settings.models import SiteSettings


class CommentsFeed(Feed):
    """评论 RSS Feed"""
    feed_type = Rss201rev2Feed
    title = "最新评论"
    description = "博客的最新评论"
    
    def link(self, request=None):
        """Feed 链接（前端 URL）"""
        from django.conf import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', None)
        if not frontend_url and request:
            # 尝试从请求中获取前端 URL
            scheme = request.scheme
            host = request.get_host()
            # 如果是开发环境，使用前端端口
            if 'localhost' in host or '127.0.0.1' in host:
                frontend_url = 'http://localhost:5173'
            else:
                frontend_url = f"{scheme}://{host}"
        return frontend_url or 'http://localhost:5173'
    
    def __init__(self):
        super().__init__()
        try:
            site_settings = SiteSettings.get_settings()
            self.title = f"{site_settings.site_name} - 最新评论"
            self.description = site_settings.site_description or "博客的最新评论"
        except Exception:
            pass
    
    def items(self):
        """返回最新的已审核评论"""
        return Comment.objects.filter(
            is_approved=True
        ).select_related('author', 'content_object').order_by('-created_at')[:30]
    
    def item_title(self, item):
        """评论标题"""
        # 获取关联对象标题
        if hasattr(item.content_object, 'title'):
            return f"{item.author.username} 评论了《{item.content_object.title}》"
        return f"{item.author.username} 的评论"
    
    def item_description(self, item):
        """评论内容"""
        return item.content
    
    def item_link(self, item):
        """评论链接（指向关联对象的前端 URL）"""
        from django.conf import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        
        # 根据内容类型生成前端 URL
        if hasattr(item.content_object, 'slug'):
            # 文章类型，使用 slug 生成链接
            return f"{frontend_url}/post/{item.content_object.slug}#comment-{item.id}"
        return f"{frontend_url}/#comment-{item.id}"
    
    def item_author_name(self, item):
        """评论者名称"""
        return item.author.username
    
    def item_pubdate(self, item):
        """评论时间"""
        return item.created_at
    
    def item_updateddate(self, item):
        """更新时间"""
        return item.updated_at


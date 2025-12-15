"""
RSS Feed 定义
"""
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from django.conf import settings
from .models import Post
from settings.models import SiteSettings


class PostsFeed(Feed):
    """文章 RSS Feed"""
    feed_type = Rss201rev2Feed
    title = "博客文章"
    description = "最新发布的博客文章"
    
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
        # 获取站点设置
        try:
            site_settings = SiteSettings.get_settings()
            self.title = f"{site_settings.site_name} - 最新文章"
            self.description = site_settings.site_description or "最新发布的博客文章"
        except Exception:
            pass
    
    def items(self):
        """返回最新的已发布文章（不包含加密文章）"""
        return Post.objects.filter(
            status='published',
            is_encrypted=False
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')[:20]
    
    def item_title(self, item):
        """文章标题"""
        return item.title
    
    def item_description(self, item):
        """文章描述（使用摘要或内容预览）"""
        if item.excerpt:
            return item.excerpt
        # 如果没有摘要，使用内容的前200字符
        if item.content:
            return item.content[:200] + '...' if len(item.content) > 200 else item.content
        return ""
    
    def item_link(self, item):
        """文章链接（前端 URL）"""
        # 前后端分离，返回前端 URL
        from django.conf import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        return f"{frontend_url}/post/{item.slug}"
    
    def item_author_name(self, item):
        """作者名称"""
        return item.author.username
    
    def item_pubdate(self, item):
        """发布时间"""
        return item.published_at or item.created_at
    
    def item_updateddate(self, item):
        """更新时间"""
        return item.updated_at
    
    def item_categories(self, item):
        """分类和标签"""
        categories = []
        if item.category:
            categories.append(item.category.name)
        categories.extend([tag.name for tag in item.tags.all()])
        return categories


class CategoryPostsFeed(Feed):
    """分类文章 RSS Feed"""
    feed_type = Rss201rev2Feed
    
    def get_object(self, request, slug):
        """获取分类对象"""
        from categories.models import Category
        return Category.objects.get(slug=slug)
    
    def title(self, obj):
        """Feed 标题"""
        try:
            site_settings = SiteSettings.get_settings()
            return f"{site_settings.site_name} - {obj.name}"
        except Exception:
            return f"博客 - {obj.name}"
    
    def description(self, obj):
        """Feed 描述"""
        return f"{obj.name}分类下的最新文章"
    
    def link(self, obj):
        """分类链接（前端 URL）"""
        from django.conf import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        return f"{frontend_url}/category/{obj.slug}"
    
    def items(self, obj):
        """返回该分类下的最新文章（不包含加密文章）"""
        return Post.objects.filter(
            category=obj,
            status='published',
            is_encrypted=False
        ).select_related('author').prefetch_related('tags').order_by('-published_at')[:20]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        if item.excerpt:
            return item.excerpt
        if item.content:
            return item.content[:200] + '...' if len(item.content) > 200 else item.content
        return ""
    
    def item_link(self, item):
        """文章链接（前端 URL）"""
        from django.conf import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        return f"{frontend_url}/post/{item.slug}"
    
    def item_author_name(self, item):
        return item.author.username
    
    def item_pubdate(self, item):
        return item.published_at or item.created_at
    
    def item_updateddate(self, item):
        return item.updated_at
    
    def item_categories(self, item):
        categories = []
        categories.extend([tag.name for tag in item.tags.all()])
        return categories


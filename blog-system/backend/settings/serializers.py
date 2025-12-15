from rest_framework import serializers
import markdown
import bleach
from .models import SiteSettings, NavigationItem


class SiteSettingsSerializer(serializers.ModelSerializer):
    """站点设置序列化器"""
    site_icon_url = serializers.SerializerMethodField()
    about_content_html = serializers.SerializerMethodField()
    
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'site_description', 'site_keywords', 'site_icon', 'site_icon_url', 
            'about_content', 'about_content_html',
            'enable_email_notification', 'email_host', 'email_port', 'email_use_tls', 
            'email_use_ssl', 'email_host_user', 'email_from',
            'updated_at'
        ]
        read_only_fields = ['updated_at']
        # 邮件密码字段不返回给前端
        extra_kwargs = {
            'email_host_password': {'write_only': True},
        }
    
    def get_site_icon_url(self, obj):
        """获取图标完整URL"""
        if obj.site_icon:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.site_icon.url)
            return obj.site_icon.url
        return None
    
    def get_about_content_html(self, obj):
        """将Markdown转换为HTML"""
        if obj.about_content:
            html = markdown.markdown(
                obj.about_content,
                extensions=['codehilite', 'fenced_code', 'tables', 'toc']
            )
            # 清理HTML，防止XSS
            allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'code', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'ul', 'ol', 'li', 'blockquote', 'strong', 'em', 'a', 'img']
            allowed_attributes = bleach.sanitizer.ALLOWED_ATTRIBUTES.copy()
            allowed_attributes['img'] = ['src', 'alt', 'title']
            return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)
        return None


class SiteSettingsUpdateSerializer(serializers.ModelSerializer):
    """站点设置更新序列化器"""
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'site_description', 'site_keywords', 'site_icon', 'about_content',
            'enable_email_notification', 'email_host', 'email_port', 'email_use_tls', 
            'email_use_ssl', 'email_host_user', 'email_host_password', 'email_from'
        ]
        extra_kwargs = {
            'email_host_password': {'write_only': True},
        }


class NavigationItemSerializer(serializers.ModelSerializer):
    """导航菜单序列化器"""
    class Meta:
        model = NavigationItem
        fields = ['id', 'name', 'url', 'is_builtin', 'is_visible', 'is_accessible', 'order']


class NavigationItemCreateUpdateSerializer(serializers.ModelSerializer):
    """导航菜单创建/更新序列化器"""
    class Meta:
        model = NavigationItem
        fields = ['name', 'url', 'is_visible', 'is_accessible', 'order']

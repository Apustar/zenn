from django.contrib import admin
from .models import SiteSettings, NavigationItem


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_description', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('site_name', 'site_description', 'site_keywords')
        }),
        ('站点图标', {
            'fields': ('site_icon',),
            'description': '支持 PNG、JPG、SVG 等格式，建议尺寸 24x24 像素'
        }),
        ('关于页面', {
            'fields': ('about_content',),
            'description': '关于页面的内容，支持 Markdown 格式'
        }),
    )

    def has_add_permission(self, request):
        """禁止添加多个实例"""
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """禁止删除"""
        return False


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_builtin', 'is_visible', 'is_accessible', 'order', 'updated_at']
    list_filter = ['is_builtin', 'is_visible', 'is_accessible']
    list_editable = ['is_visible', 'is_accessible', 'order']
    search_fields = ['name', 'url']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'url', 'order')
        }),
        ('显示控制', {
            'fields': ('is_visible', 'is_accessible'),
            'description': 'is_visible: 控制是否在导航栏显示；is_accessible: 控制是否可以通过URL访问'
        }),
        ('系统信息', {
            'fields': ('is_builtin',),
            'classes': ('collapse',)
        }),
    )

    def has_delete_permission(self, request, obj=None):
        """系统内置菜单不可删除"""
        if obj and obj.is_builtin:
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """系统内置菜单的某些字段只读"""
        if obj and obj.is_builtin:
            return ['is_builtin', 'url']
        return ['is_builtin']

    def save_model(self, request, obj, form, change):
        """保存时初始化内置菜单"""
        super().save_model(request, obj, form, change)
        # 确保内置菜单已初始化
        NavigationItem.initialize_builtin_items()

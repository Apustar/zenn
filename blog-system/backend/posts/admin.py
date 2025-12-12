from django.contrib import admin
from .models import Post, PostLike, PostView


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_top', 'is_encrypted', 'views', 'published_at', 'created_at']
    list_filter = ['status', 'is_top', 'is_encrypted', 'category', 'tags', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'published_at'
    readonly_fields = ['password_updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'cover')
        }),
        ('分类和标签', {
            'fields': ('category', 'tags')
        }),
        ('发布设置', {
            'fields': ('author', 'status', 'is_top', 'is_original', 'allow_comment', 'published_at')
        }),
        ('加密设置', {
            'fields': ('is_encrypted', 'password', 'password_updated_at'),
            'description': '设置文章加密后，访问者需要输入密码才能查看全文。密码更新时间由系统自动管理。'
        }),
        ('统计信息', {
            'fields': ('views', 'likes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__title', 'user__username']


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ['post', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']
    readonly_fields = ['post', 'ip_address', 'user_agent', 'viewed_at']

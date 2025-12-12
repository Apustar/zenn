from django.contrib import admin
from .models import Album, Photo


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ['image', 'title', 'description', 'order']


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'author', 'is_encrypted', 'order', 'created_at']
    list_filter = ['author', 'is_encrypted', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PhotoInline]
    readonly_fields = ['password_updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'slug', 'description', 'cover', 'author', 'order')
        }),
        ('加密设置', {
            'fields': ('is_encrypted', 'password', 'password_updated_at'),
            'description': '设置相册加密后，访问者需要输入密码才能查看照片。密码更新时间由系统自动管理。'
        }),
    )


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'order', 'created_at']
    list_filter = ['album', 'created_at']
    search_fields = ['title', 'description']

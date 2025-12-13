from django.contrib import admin
from .models import Music


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'album', 'is_published', 'order', 'duration', 'created_at']
    list_filter = ['is_published', 'author', 'created_at']
    search_fields = ['title', 'artist', 'album']
    list_editable = ['is_published', 'order']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'artist', 'album', 'audio_file', 'cover', 'lyrics')
        }),
        ('设置', {
            'fields': ('is_published', 'order', 'duration', 'author')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新建时
            obj.author = request.user
        super().save_model(request, obj, form, change)


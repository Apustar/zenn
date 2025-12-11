from django.contrib import admin
from .models import Moment, MomentLike


@admin.register(Moment)
class MomentAdmin(admin.ModelAdmin):
    list_display = ['content', 'author', 'likes', 'comments_count', 'visibility', 'published_at']
    list_filter = ['visibility', 'published_at', 'created_at']
    search_fields = ['content', 'author__username']
    date_hierarchy = 'published_at'


@admin.register(MomentLike)
class MomentLikeAdmin(admin.ModelAdmin):
    list_display = ['moment', 'user', 'created_at']
    list_filter = ['created_at']

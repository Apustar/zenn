from django.contrib import admin
from .models import LinkCategory, Link


@admin.register(LinkCategory)
class LinkCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'created_at']
    list_editable = ['order']


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'category', 'is_visible', 'order', 'created_at']
    list_filter = ['category', 'is_visible', 'created_at']
    search_fields = ['name', 'url', 'description']
    list_editable = ['is_visible', 'order']

from django.db import models


class LinkCategory(models.Model):
    """友链分类"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '友链分类'
        verbose_name_plural = '友链分类'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Link(models.Model):
    """友链模型"""
    name = models.CharField(max_length=100, verbose_name='网站名称')
    url = models.URLField(verbose_name='网站链接')
    description = models.TextField(blank=True, verbose_name='描述')
    logo = models.ImageField(upload_to='links/', null=True, blank=True, verbose_name='Logo')
    category = models.ForeignKey(
        LinkCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='links',
        verbose_name='分类'
    )
    order = models.IntegerField(default=0, verbose_name='排序')
    is_visible = models.BooleanField(default=True, verbose_name='是否显示')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '友链'
        verbose_name_plural = '友链'
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return self.name

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Music(models.Model):
    """音乐模型"""
    title = models.CharField(max_length=200, verbose_name='歌曲名称')
    artist = models.CharField(max_length=100, blank=True, verbose_name='艺术家')
    album = models.CharField(max_length=100, blank=True, verbose_name='专辑')
    
    # 音频文件
    audio_file = models.FileField(
        upload_to='music/audio/',
        verbose_name='音频文件',
        help_text='支持 MP3、WAV、OGG 等格式'
    )
    
    # 封面图
    cover = models.ImageField(
        upload_to='music/covers/',
        null=True,
        blank=True,
        verbose_name='封面图'
    )
    
    # 歌词（可选）
    lyrics = models.TextField(blank=True, verbose_name='歌词')
    
    # 排序和状态
    order = models.IntegerField(default=0, verbose_name='排序', help_text='数字越小越靠前')
    is_published = models.BooleanField(default=True, verbose_name='是否发布')
    
    # 元数据
    duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='时长（秒）',
        help_text='自动计算，也可手动设置'
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='musics',
        verbose_name='添加者'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '音乐'
        verbose_name_plural = '音乐'
        ordering = ['order', '-created_at']

    def __str__(self):
        if self.artist:
            return f"{self.title} - {self.artist}"
        return self.title


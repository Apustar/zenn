# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Music',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='歌曲名称')),
                ('artist', models.CharField(blank=True, max_length=100, verbose_name='艺术家')),
                ('album', models.CharField(blank=True, max_length=100, verbose_name='专辑')),
                ('audio_file', models.FileField(help_text='支持 MP3、WAV、OGG 等格式', upload_to='music/audio/', verbose_name='音频文件')),
                ('cover', models.ImageField(blank=True, null=True, upload_to='music/covers/', verbose_name='封面图')),
                ('lyrics', models.TextField(blank=True, verbose_name='歌词')),
                ('order', models.IntegerField(default=0, help_text='数字越小越靠前', verbose_name='排序')),
                ('is_published', models.BooleanField(default=True, verbose_name='是否发布')),
                ('duration', models.PositiveIntegerField(blank=True, help_text='自动计算，也可手动设置', null=True, verbose_name='时长（秒）')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='musics', to=settings.AUTH_USER_MODEL, verbose_name='添加者')),
            ],
            options={
                'verbose_name': '音乐',
                'verbose_name_plural': '音乐',
                'ordering': ['order', '-created_at'],
            },
        ),
    ]



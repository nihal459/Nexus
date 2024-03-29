# Generated by Django 4.2.2 on 2024-03-02 07:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nexusapp', '0004_alter_message_image_alter_message_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(default='Channel123', max_length=50)),
                ('message', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('video', models.FileField(blank=True, null=True, upload_to='channel_videos')),
                ('image', models.ImageField(blank=True, null=True, upload_to='channel_images')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_messages', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, related_name='Channel_Group', to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='channels', to='nexusapp.workspace')),
            ],
        ),
    ]

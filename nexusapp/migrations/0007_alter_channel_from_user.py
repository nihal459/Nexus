# Generated by Django 4.2.2 on 2024-03-03 05:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nexusapp', '0006_channel_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='from_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='channel_messages', to=settings.AUTH_USER_MODEL),
        ),
    ]

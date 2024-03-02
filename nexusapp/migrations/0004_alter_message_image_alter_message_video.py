# Generated by Django 4.2.2 on 2024-03-02 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nexusapp', '0003_workspace_message_workspace'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images'),
        ),
        migrations.AlterField(
            model_name='message',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='videos'),
        ),
    ]
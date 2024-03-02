from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=100, default='User')
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
    verified = models.BooleanField(default=False, verbose_name='Is Verified')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Date of Birth')
    mobile_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='Mobile Number')

    @property
    def imageURL(self):
        try:
            url = self.profile_picture.url
        except:
            url = ''
        return url

    def __str__(self):
        return self.username

class Workspace(models.Model):
    name = models.CharField(max_length=100)
    user = models.ManyToManyField(User, related_name='workspaces', blank=True)  # Many users can be in one workspace
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_workspaces')

    def __str__(self):
        return self.name

class Message(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to='videos', null=True, blank=True)
    image = models.ImageField(upload_to='images', null=True, blank=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)

    def __str__(self):
        return f"From: {self.from_user.username}"


class Channel(models.Model):
    channel_name = models.CharField(max_length=50, default="Channel123")
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='channel_messages')
    users = models.ManyToManyField(User, related_name='Channel_Group', blank=True)  # Many users can be in one workspace
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to='channel_videos', null=True, blank=True)
    image = models.ImageField(upload_to='channel_images', null=True, blank=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='channels', null=True, blank=True)

    def __str__(self):
        return f"From: {self.from_user}"

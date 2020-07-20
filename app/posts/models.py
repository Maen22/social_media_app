from django.db import models
from django.utils import timezone

from profiles.models import Profile


class Post(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def fullname(self):
        return self.user.full_name

    def __str__(self):
        return str(self.user.id)


class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def fullname(self):
        return self.user.full_name

    def __str__(self):
        return str(self.user)


class Comment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def fullname(self):
        return self.user.full_name

    def __str__(self):
        return str(self.user)

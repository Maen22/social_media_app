from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Post(models.Model):
    user_id = models.ForeignKey(get_user_model, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)


class Like(models.Model):
    user = models.ForeignKey(get_user_model, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)


class Comment(models.Model):
    user_id = models.ForeignKey(get_user_model, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

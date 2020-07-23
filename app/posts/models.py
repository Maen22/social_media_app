from django.db import models
from profiles.models import Profile


class Post(models.Model):
    public = 'public'
    private = 'private'
    FLAG_CHOICES = [(public, 'public'), (private, 'private')]

    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField()
    flag = models.CharField(max_length=10, choices=FLAG_CHOICES, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def fullname(self):
        return self.owner.full_name

    @property
    def num_likes(self):
        return self.like_set.count()

    @property
    def num_comments(self):
        return self.comment_set.count()

    def __str__(self):
        return str(self.owner.id)


class Like(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def fullname(self):
        return self.owner.full_name

    def __str__(self):
        return str(self.owner)


class Comment(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def fullname(self):
        return self.owner.full_name

    def __str__(self):
        return str(self.owner)

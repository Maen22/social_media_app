import datetime

from django.db import models
from django.utils import timezone

from profiles.models import Profile


class StoryManager(models.Manager):
    def create_story(self, user, text, *args, **kwargs):
        expiration_date = timezone.now() + datetime.timedelta(days=1)
        return Story.objects.create(owner=user, text=text, expiration_date=expiration_date, *args, **kwargs)


class Story(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()

    objects = StoryManager()

    @property
    def full_name(self):
        return self.owner.full_name

    def __str__(self):
        return self.owner.full_name + ' Story'

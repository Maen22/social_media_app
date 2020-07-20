from django.conf import settings
from django.db import models


class Profile(models.Model):
    male = 'M'
    female = 'F'
    GENDER_CHOICES = [(male, 'Male'), (female, 'Female')]

    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    birthday = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=False)
    address = models.CharField(max_length=255, null=True)
    picture = models.ImageField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

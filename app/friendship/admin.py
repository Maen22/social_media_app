from django.contrib import admin

# Register your models here.
from friendship.models import Friendship

admin.site.register(Friendship)
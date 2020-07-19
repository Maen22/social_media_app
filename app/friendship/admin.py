from django.contrib import admin

# Register your models here.
from friendship.models import Friendship, FriendshipRequest, Block

admin.site.register(Friendship)
admin.site.register(FriendshipRequest)
admin.site.register(Block)
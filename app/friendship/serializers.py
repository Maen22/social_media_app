from rest_framework import serializers

from profiles.serializers import ProfileSerializer
from .models import Friendship


class SpecifUserSerializer(ProfileSerializer):
    class Meta(ProfileSerializer.Meta):
        fields = ('user', 'first_name', 'last_name',)


class FriendshipSerializer(serializers.ModelSerializer):
    friend = SpecifUserSerializer(source='user_two_id')

    class Meta:
        model = Friendship
        fields = ('friend', 'created_at')


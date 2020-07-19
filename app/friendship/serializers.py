from rest_framework import serializers

from profiles.serializers import ProfileSerializer
from .models import Friendship


class SpecifUserSerializer(ProfileSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta(ProfileSerializer.Meta):
        fields = ('user', 'first_name', 'last_name',)


class FriendshipSerializer(serializers.ModelSerializer):
    user_one_id = SpecifUserSerializer()

    user_two_id = SpecifUserSerializer()

    class Meta:
        model = Friendship
        fields = ('user_one_id', 'user_two_id', 'status', 'created_at')

    def create(self, validated_data):
        return Friendship.objects.add_friend(**validated_data)

    def accept(self, validated_data):
        return Friendship.objects.accept(**validated_data)

    def reject(self, validated_data):
        return Friendship.objects.reject(**validated_data)

    def delete_friend(self, validated_data):
        return Friendship.objects.remove(**validated_data)

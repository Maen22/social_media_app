from rest_framework import serializers

from .models import FriendshipRequest, Friendship, Block
from ..accounts.serializers import UserSerializer
from ..profiles.serializers import ProfileSerializer


class SpecifUserSerializer(ProfileSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Block
        fields = ('user', 'first_name', 'last_name',)


class FriendshipRequestSerializer(serializers.ModelSerializer):
    from_user = SpecifUserSerializer()

    to_user = SpecifUserSerializer()

    class Meta:
        model = FriendshipRequest
        fields = ('from_user', 'to_user', 'created_at')

    def create(self, validated_data):
        return Friendship.objects.add_friend(**validated_data)

    def accept(self, validated_data):
        return FriendshipRequest.objects.accept(**validated_data)

    def reject(self, validated_data):
        return FriendshipRequest.objects.accept(**validated_data)


class FriendshipSerializer(serializers.ModelSerializer):
    from_user = SpecifUserSerializer()
    to_user = SpecifUserSerializer()

    class Meta:
        model = Friendship
        fields = ('from_user', 'to_user', 'created_at',)

    def delete_friend(self, validated_data):
        return Friendship.objects.remove(**validated_data)


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ('blocked', 'created_at',)

    def block(self, validated_data):
        return Block.objects.add_block(**validated_data)

    def remove_block(self, validated_data):
        return Block.objects.remove_block(**validated_data)

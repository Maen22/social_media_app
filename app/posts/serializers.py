from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Post


def string_not_empty(value):
    text = value
    valid = text.strip()
    if not valid:
        return ValidationError('Comment must be filled with text')


class LikeSerializer(serializers.Serializer):
    owner = serializers.CharField()


class CommentSerializer(LikeSerializer):
    text = serializers.CharField()


class CreateCommentSerializer(serializers.Serializer):
    text = serializers.CharField(required=True)


class PostDetailSerializer(serializers.ModelSerializer):
    # user = serializers.IntegerField()
    owner = serializers.CharField()
    likes = serializers.IntegerField()
    comments = serializers.IntegerField()

    class Meta:
        model = Post
        fields = ('owner', 'likes', 'comments', 'created_at',)
        read_only_fields = ('owner', 'likes', 'comments', 'created_at',)


from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Post


def string_not_empty(value):
    text = value
    valid = text.strip()
    if not valid:
        return ValidationError('Comment must be filled with text')


class LikeSerializer(serializers.Serializer):
    fullname = serializers.CharField()


class CommentSerializer(serializers.Serializer):
    fullname = serializers.CharField()
    text = serializers.CharField()

class CreateCommentSerializer(serializers.Serializer):
    text = serializers.CharField(required=True)


class PostDetailSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField()
    likes = serializers.IntegerField()
    comments = serializers.IntegerField()

    class Meta:
        model = Post
        fields = ('user', 'text', 'likes', 'comments', 'created_at',)
        read_only_fields = ('user', 'likes', 'comments', 'created_at',)


class PostLikesSerializer(serializers.Serializer):
    likes = LikeSerializer(many=True)

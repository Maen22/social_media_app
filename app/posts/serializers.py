from rest_framework import serializers

from .models import Comment, Like, Post


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('user', 'post', 'created_at',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('user', 'text',)
        read_only_fields = ('user',)

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)


class PostSerializer(serializers.ModelSerializer):
    likes = LikeSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Post
        fields = ('user', 'text', 'created_at',)

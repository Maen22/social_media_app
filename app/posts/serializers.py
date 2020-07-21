from rest_framework import serializers

from .models import Post, Like, Comment


class BaseSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.full_name')

    class Meta:
        model = None
        fields = ('owner', 'created_at',)


class LikeSerializer(BaseSerializer):
    class Meta:
        model = Like


class CommentSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Comment
        fields = BaseSerializer.Meta.fields + ('text', )


class CreateCommentSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=True)


class PostDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.full_name')
    likes = serializers.ReadOnlyField(source='num_likes')
    comments = serializers.ReadOnlyField(source='num_comments')

    class Meta:
        model = Post
        fields = ('id', 'owner', 'text', 'likes', 'comments', 'created_at',)
        extra_kwargs = {'likes': {'read_only': True},
                        'comments': {'read_only': True}}

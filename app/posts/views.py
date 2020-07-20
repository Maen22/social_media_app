from django.shortcuts import get_object_or_404
from rest_framework import mixins, filters, status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Post, Like, Comment
from .serializers import PostDetailSerializer, LikeSerializer, CommentSerializer, CreateCommentSerializer


class PostViewSet(GenericViewSet,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PostDetailSerializer
    queryset = Post.objects.all()

    filter_backends = [filters.SearchFilter]
    search_fields = ['text']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def list_posts(self, request):
        posts = Post.objects.all()
        result = []
        for post in posts:
            num_likes = post.like_set.count()
            num_comments = post.comment_set.count()
            data = {
                'user': post.user.pk,
                'text': post.text,
                'likes': num_likes,
                'comments': num_comments
            }
            result.append(data)

        serializer = PostDetailSerializer(data=result, many=True)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):  # dont forget the unlike and delete comment
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user.profile, post=post)
        if created:
            return Response('You hit the like button', status=status.HTTP_200_OK)
        return Response('Like already exists', status=status.HTTP_208_ALREADY_REPORTED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        serializer = CreateCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment, created = Comment.objects.get_or_create(user=request.user.profile, post=post,
                                                         text=serializer.data['text'])
        if created:
            return Response('Your comment is submitted', status=status.HTTP_200_OK)
        return Response('comment with this text already exists', status=status.HTTP_208_ALREADY_REPORTED)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def post_detail(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        user = post.user.pk
        num_likes = post.like_set.count()
        num_comments = post.comment_set.count()
        data = {
            'user': user,
            'text': post.text,
            'likes': num_likes,
            'comments': num_comments
        }
        serializer = PostDetailSerializer(post, data=data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def post_likes_detail(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        likes = list(post.like_set.all())

        likes = [{'fullname': like.fullname} for like in likes]
        serializer = LikeSerializer(data=likes, many=True)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def post_comments_detail(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        comments = list(post.comment_set.all())
        print(comments)

        serializer = CommentSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

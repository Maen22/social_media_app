from django.shortcuts import get_object_or_404
from rest_framework import mixins, filters, status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Post, Like, Comment
from .serializers import PostDetailSerializer, CreateCommentSerializer, LikeSerializer, CommentSerializer


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

    pagination_classes = (PageNumberPagination,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)

    def paginated_data(self, qs):
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        if self.action == 'post_likes_detail':
            return LikeSerializer(*args, **kwargs)
        elif self.action == 'post_comments_detail':
            return CommentSerializer(*args, **kwargs)
        return self.serializer_class(*args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def list_posts(self, request):
        posts = Post.objects.all()
        result = []
        for post in posts:
            num_likes = post.like_set.count()
            num_comments = post.comment_set.count()
            data = {
                'owner': post.fullname,
                'text': post.text,
                'likes': num_likes,
                'comments': num_comments
            }
            result.append(data)

        return self.paginated_data(result)

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
        num_likes = post.like_set.count()
        num_comments = post.comment_set.count()
        data = {
            'owner': post.fullname,
            'text': post.text,
            'likes': num_likes,
            'comments': num_comments
        }

        serializer = PostDetailSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def post_likes_detail(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        likes = list(post.like_set.all())

        likes = [{'owner': like.fullname} for like in likes]
        return self.paginated_data(likes)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def post_comments_detail(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        comments = list(post.comment_set.all())
        result = []
        for comment in comments:
            data = {
                'owner': comment.fullname,
                'text': comment.text
            }
            result.append(data)
        return self.paginated_data(result)

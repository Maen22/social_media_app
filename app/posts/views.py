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

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset

        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
        if len(likes) > 1:
            likes = [{'fullname': like.fullname} for like in likes]
            serializer = LikeSerializer(data=likes, many=True)
            serializer.is_valid()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if len(likes) == 0:
            return Response("No Likes for this post yet", status=status.HTTP_200_OK)
        like = {'fullname': likes[0].fullname}
        serializer = LikeSerializer(data=like)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def post_comments_detail(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        comments = list(post.comment_set.all())
        print(comments)
        if len(comments) > 1:
            newComments = []
            for comment in comments:
                newComments.append({'fullname': comment.fullname, 'text': comment.text})
            # comments = [{('fullname'),('text'): (comment.fullname, comment.text)} for comment in comments]
            print(newComments)
            serializer = CommentSerializer(data=newComments, many=True)
            serializer.is_valid()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if len(comments) == 0:
            return Response("No comments for this post yet", status=status.HTTP_200_OK)

        comment = {'fullname': comments[0].fullname,
                   'text': comments[0].text}

        serializer = CommentSerializer(data=comment)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)

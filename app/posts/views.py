from rest_framework import mixins, filters, status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Post, Like, Comment
from .serializers import PostSerializer, CommentSerializer


class PostViewSet(GenericViewSet,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
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
        post = Post.objects.get(pk=pk)
        like, created = Like.objects.get_or_create(user=request.user.profile, post=post)
        if created:
            post.like_set.add(like)
            return Response('You hit the like button', status=status.HTTP_200_OK)
        return Response('Like already exists', status=status.HTTP_208_ALREADY_REPORTED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = Post.objects.get(pk=pk)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid()
        post.comment_set.add(serializer.save())
        return Response('You commented on the post successfully', status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def likes(self, request, pk=None):
        post = Post.objects.get(pk=pk)
        num_likes = Like.objects.filter(post=post).all().count()
        return Response(f'This post has {num_likes} likes', status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        post = Post.objects.get(pk=pk)
        num_comments = Comment.objects.filter(post=post).all().count()
        return Response(f'This post has {num_comments} comments', status=status.HTTP_200_OK)

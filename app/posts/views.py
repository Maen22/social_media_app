from django.db.models import Q
from rest_framework import mixins, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from friendship.models import Friendship
from .models import Post, Like, Comment
from .serializers import PostDetailSerializer, CreateCommentSerializer, LikeSerializer, CommentSerializer

serializers = {
    'post_likes_detail': LikeSerializer,
    'post_comments_detail': CommentSerializer
}


class PostPermission(permissions.BasePermission):

    def are_friends(self, user1, user2, request):
        result = Friendship.objects.filter(
            Q(user_one_id=user1, user_two_id=user2, status=2)
            | Q(user_one_id=user2, user_two_id=user1, status=2)) \
            .distinct().all()
        if result or user2.user == request.user:
            return True
        return False

    def is_post_public(self, post):
        if post.flag == 'public':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if self.is_post_public(obj):
            return True
        return self.are_friends(request.user.profile, obj.owner, request)


class PostViewSet(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = Post.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['text']
    pagination_classes = (PageNumberPagination,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)

    def get_serializer(self, *args, **kwargs):
        return serializers.get(self.action, PostDetailSerializer)(*args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, ])
    def create_post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, ])
    def edit_post(self, request, pk=None, *args, **kwargs):
        post = Post.objects.filter(pk=pk)
        if post.owner == request.user.profile:
            return self.partial_update(request, *args, **kwargs)
        return Response("You do not have permission to perform this action.")

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, PostPermission, ])
    def list_posts(self, request):
        self.queryset = Post.objects.all()
        return self.list(request=request)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, PostPermission, ])
    def like(self, request, pk=None):  # dont forget the unlike and delete comment
        post = Post.objects.filter(pk=pk)
        like, created = Like.objects.get_or_create(owner=request.user.profile, post=post)
        if created:
            return Response('You hit the like button', status=status.HTTP_200_OK)
        return Response('Like already exists', status=status.HTTP_208_ALREADY_REPORTED)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, PostPermission, ])
    def unlike(self, request, pk=None):  # dont forget the unlike and delete comment
        post = Post.objects.filter(pk=pk)
        self.queryset = Like.objects.filter(owner=request.user.profile, post=post)
        if self.queryset:
            self.destroy(request=request)
            return Response('You hit the unlike button', status=status.HTTP_200_OK)
        return Response('Like already does not exists', status=status.HTTP_208_ALREADY_REPORTED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, PostPermission, ])
    def comment(self, request, pk=None):
        post = Post.objects.filter(pk=pk)
        serializer = CreateCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment, created = Comment.objects.get_or_create(owner=request.user.profile, post=post,
                                                         text=serializer.data['text'])
        if created:
            return Response('Your comment is submitted', status=status.HTTP_200_OK)
        return Response('comment with this text already exists', status=status.HTTP_208_ALREADY_REPORTED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, PostPermission, ])
    def uncomment(self, request, pk=None):
        """
            Takes a query_param (comment_id) to specify the comment that
            will be deleted
        """

        post = Post.objects.filter(pk=pk)
        comment_id = request.query_params.get('comment_id', None)
        self.queryset = Comment.objects.filter(id=comment_id, owner=request.user.profile, post=post)
        if self.queryset:
            self.destroy(request=request)
            return Response('Your comment has been deleted', status=status.HTTP_200_OK)
        return Response('Comment already does not exists', status=status.HTTP_208_ALREADY_REPORTED)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, PostPermission, ])
    def post_detail(self, request, pk=None):
        # self.queryset = self.get_object()
        self.queryset = Post.objects.filter(pk=pk)
        return self.retrieve(request=request)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, PostPermission, ])
    def post_likes_detail(self, request, pk=None):
        post = Post.objects.filter(pk=pk)
        self.queryset = post.like_set.all()
        return self.list(request)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, PostPermission, ])
    def post_comments_detail(self, request, pk=None):
        post = Post.objects.filter(pk=pk)
        self.queryset = post.comment_set.all()
        return self.list(request)

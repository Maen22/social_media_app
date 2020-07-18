from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Friendship, FriendshipRequest, Block
from .serializers import FriendshipRequestSerializer, FriendshipSerializer, BlockSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status


class FriendshipRequestViewSet(GenericViewSet,
                               mixins.ListModelMixin,
                               mixins.RetrieveModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendshipRequestSerializer
    queryset = FriendshipRequest.objects.all()

    def get_queryset(self):
        return self.queryset.filter(from_user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_friend(self, request, pk=None):
        serializer = FriendshipRequestSerializer(from_user=request.user, to_user=pk)
        serializer.is_valid(raise_exception=True)
        serializer.create(validated_data=serializer.validated_data)
        return Response("Friendship request has been sent", status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept_request(self, request, pk=None):
        serializer = FriendshipRequestSerializer(from_user=request.user, to_user=pk)
        serializer.is_valid(raise_exception=True)
        serializer.accept(validated_data=serializer.validated_data)
        return Response("Friendship request has been accepted", status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject_request(self, request, pk=None):
        serializer = FriendshipRequestSerializer(from_user=request.user, to_user=pk)
        serializer.is_valid(raise_exception=True)
        serializer.reject(validated_data=serializer.validated_data)
        return Response("Friendship request has been rejected", status=status.HTTP_200_OK)


class FriendshipRequestsToMeViewSet(GenericViewSet,
                                    mixins.ListModelMixin, ):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendshipRequestSerializer

    def get_queryset(self):
        return self.queryset.filter(to_user=self.request.user)


class FriendshipViewSet(GenericViewSet,
                        mixins.ListModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendshipSerializer
    queryset = Friendship.objects.all()

    def get_queryset(self):
        return self.queryset.filter(from_user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def delete_friend(self, request, pk=None):
        serializer = FriendshipSerializer(from_user=request.user, to_user=pk)
        serializer.is_valid(raise_exception=True)
        serializer.delete_friend(validated_data=serializer.validated_data)
        return Response("Friend has been deleted", status=status.HTTP_204_NO_CONTENT)


class BlockViewSet(GenericViewSet,
                   mixins.ListModelMixin):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = BlockSerializer
    queryset = Block.objects.all()

    def get_queryset(self):
        return self.queryset.filter(blocker=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def block_friend(self, request, pk=None):
        serializer = BlockSerializer(blocker=request.user, blocked=pk)
        serializer.is_valid(raise_exception=True)
        serializer.block(validated_data=serializer.validated_data)
        return Response("Friend has been blocked", status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def remove_block(self, request, pk=None):
        serializer = BlockSerializer(blocker=request.user, blocked=pk)
        serializer.is_valid(raise_exception=True)
        serializer.remove_block(validated_data=serializer.validated_data)
        return Response("User has been unblocked", status=status.HTTP_200_OK)

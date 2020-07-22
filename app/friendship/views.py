from django.db.models import Q
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import User
from .models import Friendship
from .serializers import FriendshipSerializer


class FriendshipViewSet(GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = FriendshipSerializer
    queryset = Friendship.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset
        return self.queryset.filter(
            Q(user_one_id=self.request.user.profile)
            | Q(user_two_id=self.request.user.profile)
        ).distinct().all()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_friends(self, request):
        self.queryset = self.get_queryset().filter(status=2).order_by('-id')
        return self.list(request=request)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def add_friend(self, request, pk=None):
        Friendship.objects.add_friend(from_user=request.user.profile,
                                      to_user=User.objects.get(pk=pk).profile)
        return Response("Friendship request has been sent", status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept_request(self, request, pk=None):
        Friendship.objects.accept(user_one_id=request.user.profile, user_two_id=User.objects.get(pk=pk).profile)
        return Response("Friendship request has been accepted", status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject_request(self, request, pk=None):
        Friendship.objects.reject(user_one_id=request.user.profile, user_two_id=User.objects.get(pk=pk).profile)
        return Response("Friendship request has been rejected", status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def delete_friend(self, request, pk=None):
        Friendship.objects.remove_friend(user_one_id=request.user.profile, user_two_id=User.objects.get(pk=pk).profile)
        return Response("Friend has been deleted", status=status.HTTP_204_NO_CONTENT)

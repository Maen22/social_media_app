from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from rest_framework import permissions, mixins
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer, AuthTokenSerializer, PasswordChangeSerializer, CreateUserSerializer, \
    UpdateUserSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRelatedView(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """
    A view for the superusers and authenticated users to retrieve ('GET') or update ('PUT', 'PATCH') or soft delete (
    'DELETE') the users data through the users/ url for superusers, and 'users/me/' url for the authenticated users
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'


    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def create_user(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(validated_data=serializer.validated_data)
        token = default_token_generator.make_token(user)
        mail_subject = 'Activate your account.'

        message = 'link: ' + f"http://127.0.0.1:8000/activate/{user.id}/{token}"
        to_email = serializer.data['email']
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()
        serializer.data['detail'] = "Please check your email address to complete the registration"
        return Response("Please check your email address to complete the registration", status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user=user)
        return Response(tokens, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.validated_data['user']
        instance.set_password(serializer.data.get('new_password'))
        instance.save()

        return Response('Password changed successfully')

    # url_path for customizing all the methods
    @action(detail=False, methods=['get', 'put', 'patch', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def user_details(self, request):

        user = request.user

        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'PUT':
            serializer = UpdateUserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.update(instance=user, validated_data=serializer.validated_data)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        if request.method == 'PATCH':
            serializer = UpdateUserSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.update(instance=user, validated_data=serializer.validated_data)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            user.is_active = False
            user.save()
            return Response("User is deactivated", status=status.HTTP_204_NO_CONTENT)


class ActivateUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, token):

        user = get_object_or_404(User, id=pk)

        if user.is_active:
            return Response('already activated', status=status.HTTP_208_ALREADY_REPORTED)

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response('Thank you for your email confirmation. Now you can login to your account.',
                            status=status.HTTP_202_ACCEPTED)
        else:
            return Response('Activation link is invalid!', status=status.HTTP_400_BAD_REQUEST)

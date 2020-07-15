from rest_framework import serializers

from accounts.serializers import UserSerializer
from profiles.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'birthday', 'gender', 'created_at')


class SearchProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'birthday', 'gender', 'user',)

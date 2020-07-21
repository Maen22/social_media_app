from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'birthday', 'gender', "address", 'picture',)


class SearchProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Profile
        fields = ('user', 'first_name', 'last_name', 'birthday', 'gender', "address", 'picture',)

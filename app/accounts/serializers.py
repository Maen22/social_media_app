from django.contrib.auth import get_user_model, authenticate, password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from validate_email import validate_email


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class CreateUserSerializer(UserSerializer):
    confirm_password = serializers.CharField(max_length=128, allow_blank=False, required=True, write_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['confirm_password']

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        # self.data.pop('confirm_password')
        return get_user_model().objects.create_user(**validated_data)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        email = attrs.get('email')

        email_is_valid = validate_email(email, check_mx=True)

        if not email_is_valid:
            raise serializers.ValidationError(_('No MX record for domain found. (The email doesnt exist)'))

        password_validation.validate_password(password=password)

        if password != confirm_password:
            raise serializers.ValidationError(_("Passwords doesn't match, Try again"))

        return attrs


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email']

    def validate(self, attrs):
        """
        Checking the email when updating it
        """

        email = attrs.get('email')
        email_is_valid = validate_email(email, check_mx=True)
        if not email_is_valid:
            raise serializers.ValidationError(_('No MX record for domain found. (The email doesnt exist)'))
        return attrs


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for the user authentication object
    """

    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """
        Validate and authenticate the user
        """

        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, allow_blank=False, required=True)
    new_password = serializers.CharField(max_length=128, allow_blank=False, required=True)
    confirm_password = serializers.CharField(max_length=128, allow_blank=False, required=True)

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        user = self.context.get('request').user
        if not user.check_password(old_password):
            raise serializers.ValidationError(_("Old password doesn't match"))

        password_validation.validate_password(password=new_password, user=user)

        if not new_password == confirm_password:
            raise serializers.ValidationError(_("Passwords doesn't match"))

        attrs['user'] = user

        return attrs

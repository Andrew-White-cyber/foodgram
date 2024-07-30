import re
import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.text import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import Follow

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserPasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для смены пароля."""
    class Meta:
        model = User
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей(создание)."""

    avatar = Base64ImageField(use_url=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'first_name', 'last_name', 'avatar',]
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'required': False},
            }

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Using "me" as a username is not allowed.'
            )
        pattern = re.compile(r'^[\w.@+-]+\Z')
        if not pattern.match(value):
            raise serializers.ValidationError('Invalid username!')
        return value

    def validate(self, data):
        email = data.get('email', None)
        username = data.get('username', None)
        user_username = User.objects.filter(username=username)
        user_email = User.objects.filter(email=email)
        if User.objects.filter(username=username, email=email):
            return data
        if user_email.exists():
            raise serializers.ValidationError('Email taken')
        if user_username.exists():
            raise serializers.ValidationError('Username taken')
        return data

    def to_representation(self, instance):
        return {
            'email': instance.email,
            'id': instance.id,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
        }


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор получения токена."""

    email = serializers.EmailField()

    class Meta:
        fields = (
            'email',
        )


class UserListSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей(список)."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(use_url=True, required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if user.is_anonymous:
                return False
            return Follow.objects.filter(user=user, following=obj).exists()
        return False

import re
import base64

from rest_framework import serializers, status
from django.core.files.base import ContentFile
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.text import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import Follow
from recipes.models import Recipe

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id',)


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
        first_name = data.get('first_name', None)
        last_name = data.get('last_name', None)
        if first_name is None or last_name is None:
            raise serializers.ValidationError('first or last name is missing !')
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


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(UserListSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        following = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(following=following, user=user).exists():
            raise serializers.ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == following:
            raise serializers.ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data

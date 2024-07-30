from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Recipe, Tag, Ingredients
from users.models import Follow


User = get_user_model()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецептов."""

    class Meta:
        model = Recipe
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиентов."""

    class Meta:
        model = Ingredients
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели подписок."""

    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    user = serializers.SlugRelatedField(
        slug_field='username',
        required=False,
        queryset=User.objects.all(),
    )

    class Meta:
        fields = ('user', 'following')
        model = Follow

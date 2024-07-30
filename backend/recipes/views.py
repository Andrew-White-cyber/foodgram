from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from django.contrib.auth import get_user_model

from .models import Recipe, Tag, Ingredients
from users.models import Follow
from .mixins import ListRetriveViewSet
from .serializers import RecipeSerializer, IngredientsSerializer, TagSerializer, FollowSerializer


User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class TagViewSet(ListRetriveViewSet):
    """Вьюсет модели тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientsViewSet(ListRetriveViewSet):
    """Вьюсет модели ингридиентов."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class FollowViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ВьюСет для модели подписок."""

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ('following__username',)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        return {
            'request': self.request,
        }

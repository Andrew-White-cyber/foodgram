from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


from .serializers import (
    UserSerializer, TokenObtainSerializer, UserPasswordSerializer,
    UserListSerializer, RecipeMinifiedSerializer, SubscribeSerializer,
    AvatarSerializer
)
from users.models import Follow
from foodgram_backend import settings, pagination

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет пользователей."""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = pagination.CustomPagination

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSerializer
        return UserListSerializer

    def to_representation(self, instance):
        """Отобразить ограниченное кол-во рецептов."""
        representation = super().to_representation(instance)
        recipes_limit = self.request.query_params.get('recipes_limit', None)

        if recipes_limit is not None:
            recipes_queryset = instance.recipes.all()[:recipes_limit]
        else:
            recipes_queryset = instance.recipes.all()

        representation['recipes'] = RecipeMinifiedSerializer(recipes_queryset,
                                                             many=True).data
        return representation

    @action(
        methods=['POST',], permission_classes=(IsAuthenticated,),
        detail=False
    )
    def set_password(self, request):
        """Изменение пароля."""
        serializer = UserPasswordSerializer(
            request.user, data=request.data,
            partial=True, context={'request': request}
        )
        user = request.user
        data = request.data
        if user.password != data['current_password']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET', 'PATCH'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Профиль пользователя."""
        serializer = UserListSerializer(request.user)
        if request.method == 'GET':
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)

    @action(
        detail=False, methods=['put', 'delete'],
        permission_classes=[IsAuthenticated], url_path='me/avatar'
    )
    def avatar(self, request):
        """Аватар."""
        user = request.user
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = AvatarSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            avatar_url = serializer.data.get('avatar')
            full_avatar_url = f'{avatar_url}'
            response_data = {'avatar': full_avatar_url}
            # breakpoint()
            return Response(response_data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            if not user.avatar:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user.avatar.delete(save=True)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated], url_path='subscribe'
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('pk')
        following = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = SubscribeSerializer(following,
                                             data=request.data,
                                             context={"request": request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, following=following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                subscription = Follow.objects.get(
                    user=user, following=following
                )
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    """FBV получения токена."""
    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    user = User.objects.get(email=data['email'])
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'auth_token': token.key}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """FBV удаления токена(logout)."""
    if request.method == 'POST':
        try:
            request.user.auth_token.delete()
            return Response(
                {'message': 'Successfully logged out.'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token


from .serializers import UserSerializer, TokenObtainSerializer, UserPasswordSerializer, UserListSerializer
from users.models import Follow
from recipes.serializers import FollowSerializer
from foodgram_backend import settings

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет пользователей."""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSerializer
        return UserListSerializer

    @action(methods=['POST',], permission_classes=(IsAuthenticated,), detail=False)
    def set_password(self, request):
        """Изменение пароля."""
        serializer = UserPasswordSerializer(request.user, data=request.data, partial=True)
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
                if 'role' not in request.data:
                    serializer = UserSerializer(
                        request.user,
                        data=request.data,
                        partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'delete'], permission_classes=[IsAuthenticated], url_path='me/avatar')
    def avatar(self, request):
        """Аватар."""
        user = request.user
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            avatar_url = serializer.data.get('avatar')
            full_avatar_url = f'{settings.MEDIA_URL}{avatar_url}'
            response_data = {'avatar': full_avatar_url}
            return Response(response_data, status=status.HTTP_200_OK)
        if request.method =='DELETE':
            if not user.avatar:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            user.avatar.delete(save=True)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, pk):
        """Подписаться."""
        user = request.user
        following = get_object_or_404(User, id=pk)
        subscription = Follow.objects.filter(user=user, following=following)
        # breakpoint()
        if request.method == 'POST':
            if subscription.exists():
                return Response('Уже подписан !', status=status.HTTP_400_BAD_REQUEST)
            if user == following:
                return Response('Нельзя подписаться на самого себя !', status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(following, context={'request': request})
            Follow.objects.create(user=user, following=following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response('Вы не подписаны на данного пользователя !', status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Подписки."""
        user = request.user
        follows = user.followers.all()
        page = self.paginate_queryset(follows)
        serializer = FollowSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    """FBV получения токена."""
    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    user = User.objects.get(email=data['email'])
    # token = RefreshToken.for_user(user)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'auth_token': token.key}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """FBV удаления токена(logout)."""
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

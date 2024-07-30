from django.urls import path
from rest_framework.routers import SimpleRouter
from django.urls import include

from .views import TagViewSet, RecipeViewSet, IngredientsViewSet
from users.views import UserViewSet, get_jwt_token, user_logout


router_v1 = SimpleRouter()
router_v1.register(r'tags', TagViewSet)
router_v1.register(r'recipes', RecipeViewSet)
router_v1.register(r'ingredients', IngredientsViewSet)
router_v1.register(r'users', UserViewSet)

urlpatterns = [
    # path('auth/', include('djoser.urls.authtoken')),
    path('auth/token/login/', get_jwt_token),
    path('auth/token/logout/', user_logout),
    path('', include(router_v1.urls)),
]

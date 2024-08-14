from django.contrib import admin

from .models import MyUser
from recipes.models import (
    Ingredients, Tag, Recipe, ShoppingCart,
    FavoriteRecipe, RecipeIngredients, RecipeTags
)


class MyUserAdmin(admin.ModelAdmin):
    """Кастомный класс админ модели Myuser."""

    search_fields = ('email', 'username',)


class IngredientsAdmin(admin.ModelAdmin):
    """Кастомный класс админ модели Ingredients."""

    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """Кастомный класс админ модели Recipe."""

    list_display = ('name', 'author', 'added_in_favorites')
    search_fields = ('name', 'author',)
    list_filter = ('tags',)

    @admin.display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return obj.users_recipes.count()


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(FavoriteRecipe)
admin.site.register(RecipeIngredients)
admin.site.register(RecipeTags)

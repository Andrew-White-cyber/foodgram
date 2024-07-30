from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    """Модель тэгов."""

    name = models.CharField('Название', max_length=16, unique=True)
    slug = models.SlugField(unique=True)


class Ingredients(models.Model):
    """Модель ингридиентов."""

    name = models.CharField('Название', max_length=16, unique=True)
    measurement_unit = models.CharField('Единица измерения', max_length=10)


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User, related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=256)
    image = models.ImageField(
        upload_to='recipes/images/',
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(Ingredients,
                                         through='RecipeIngredients')
    tags = models.ManyToManyField(Tag, through='RecipeTags')
    coocking_time = models.IntegerField(
        'Время приготовления в минутах.',
        validators=[
            MinValueValidator(
                1,
                'Нельзя приготовить быстрее чем за 1 минуту !'
            )
        ]
    )


class RecipeIngredients(models.Model):
    """Промежуточная модель рецепт - ингридиент."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredients = models.ForeignKey(Ingredients, on_delete=models.CASCADE)


class RecipeTags(models.Model):
    """Промежуточная модель рецепт - тэг."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)


class FavoriteRecipe(models.Model):
    """
    Класс избранных рецептов пользователя.
    Модель связывает Recipe и User.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='users_recipes',
        verbose_name='Рецепт',
    )

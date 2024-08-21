from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

# from .serializers import MAX_VALUE, MIN_VALUE

User = get_user_model()

MIN_VALUE = 1
MAX_VALUE = 32000


class Tag(models.Model):
    """Модель тэгов."""

    name = models.CharField('Название', max_length=16, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name


class Ingredients(models.Model):
    """Модель ингридиентов."""

    name = models.CharField('Название', max_length=16, unique=True)
    measurement_unit = models.CharField('Единица измерения', max_length=10)

    def __str__(self) -> str:
        return self.name


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
                                         through='RecipeIngredients',
                                         related_name='recipes',
                                         )
    tags = models.ManyToManyField(Tag, through='RecipeTags')
    cooking_time = models.IntegerField(
        'Время приготовления в минутах.',
        validators=[
            MinValueValidator(
                MIN_VALUE,
                f'Нельзя приготовить быстрее чем за {MIN_VALUE}'
            ),
            MaxValueValidator(
                MAX_VALUE,
                f'Время приготовления не может быть выше {MAX_VALUE}'
            )
        ]
    )

    def __str__(self) -> str:
        return self.name


class RecipeIngredients(models.Model):
    """Промежуточная модель рецепт - ингридиент."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredients = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message=f'Минимальное количество {MIN_VALUE}!'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message=f'Максимальное количество {MAX_VALUE}!'
            )
        ]
    )


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


class ShoppingCart(models.Model):
    """ Модель Корзина покупок """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в Корзину покупок'

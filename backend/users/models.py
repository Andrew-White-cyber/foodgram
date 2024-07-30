from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    """Кастомная модель пользователя."""

    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        blank=True,
        null=True,
        default=None
    )


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        MyUser, on_delete=models.CASCADE,
        related_name='followers',
        blank=True, null=True
    )
    following = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='following',
        blank=True,
        null=True
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('following',),
                name='following_unique'
            ),
        )

    def __str__(self) -> str:
        return self.user.username

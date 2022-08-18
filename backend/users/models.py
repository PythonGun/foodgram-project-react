from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    username = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        validators=(validate_username,)
    )

    email = models.EmailField(
        max_length=255,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Электронная почта'
    )

    first_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Имя пользователя'
    )

    last_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Фамилия пользователя'
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']

    def __str__(self):
        return f'{self.email} {self.first_name} {self.last_name}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_subscription",
            )
        ]

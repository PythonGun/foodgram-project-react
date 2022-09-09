from django.core import validators
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название тэга',
    )

    color = models.CharField(
        max_length=7,
        default='#49B64E',
        unique=True,
        verbose_name='Цвет тэга HEX'
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Ссылка'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название ингредиента'
    )

    measurement_unit = models.CharField(
        max_length=255,
        verbose_name='Единица измерения ингредиента'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор',
    )

    name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Название рецепта',
    )

    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        verbose_name='Изображение рецепта',
    )

    text = models.CharField(
        max_length=255,
        blank=False,
        null=True,
        verbose_name='Описание рецепта',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )

    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipe',
        verbose_name='Тэги рецепта'
    )

    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        blank=False,
        verbose_name='Время приготовления (мин)'
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент',
    )

    amount = models.PositiveSmallIntegerField(
        validators=[validators.MinValueValidator(
            1, message='Укажите не менее 1'
        )],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            )
        ]


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тэг'
    )

    class Meta:
        verbose_name = 'Тэг',
        verbose_name_plural = 'Тэги',
        constraints = (
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='unique_tag_for_recipe'
            ),
        )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избарнный рецепт',
        verbose_name_plural = 'Избранные рецепты',
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe',
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_cart',
            )
        ]

from django.core import validators
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

ORANGE = "#E26C2D"
GREEN = "#49B64E"
PURPLE = "#8775D2"

COLORS_TAGS = [
    (ORANGE, 'Оранжевый'),
    (GREEN, 'Зеленый'),
    (PURPLE, 'Фиолетовый')
]


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название тэга',
    )
    
    color = models.CharField(
        choices=COLORS_TAGS,
        max_length=7,
        default=ORANGE,
        unique=True,
        verbose_name='Цвет тэга'
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

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    
    name = models.CharField(
        max_length=150,
        verbose_name='Название рецепта',
    )
    
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение рецепта',
    )
    
    text = models.CharField(
        max_length=255,
        verbose_name='Описание рецепта',
    )
    
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (мин)'
    )
    
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты для рецепта'
    )
    
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации рецепта'
    )
    
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        verbose_name='Тэги рецепта'
    )
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
    
    def __str__(self):
        return f'{self.name}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )

    amount = models.PositiveSmallIntegerField(
        validators=[validators.MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return f'Для рецепта {self.recipe} необходимы следующие ингрредиенты: {self.ingredient}'


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
                fields=('tag', 'recipe'),
                name='unique_tag_for_recipe'
            ),
        )

    def __str__(self):
        return f'Тэг рецепта {self.recipe}: {self.tag}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorite',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избарнный рецепт',
        verbose_name_plural = 'Избранные рецепты',
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у пользователя {self.user}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_list',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        ordering = ['-id']

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list'
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'

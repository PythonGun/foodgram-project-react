from tabnanny import verbose
from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator


User = get_user_model()

class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название тэга',
        unique=True
    )
    
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет тэга',
        unique=True,
    )
    
    slug = models.SlugField(
        max_length=100,
        verbose_name='Ссылка',
        unique=True
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
        verbos_name = 'Ингредиент'
        verbos_name_plural = 'Ингредиенты'
    
    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipes(models.Model):
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
    
    description = models.CharField(
        max_length=255,
        verbose_name='Описание рецепта',
    )
    
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (минут)'
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
    
    def __str__(self):
        return f'{self.author.email}, {self.name}'

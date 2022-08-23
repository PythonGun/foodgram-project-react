from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagInLine(admin.TabularInline):
    model = RecipeTag
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'text', 'pub_date',
    )
    search_fields = (
        'name', 'cooking_time', 'author',
    )
    list_filter = (
        'pub_date', 'tags', 'author',
    )
    inlines = (RecipeIngredientInLine, RecipeTagInLine,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'color', 'slug',
    )
    search_fields = ('name', 'slug',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit',
    )
    search_fields = (
        'name', 'measurement_unit',
    )
    list_filter = ('name',)
    empty_value_display = '-пусто-'

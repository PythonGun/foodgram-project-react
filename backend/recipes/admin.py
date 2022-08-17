from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingList, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'description', 'author', 'description', 'pub_date')
    search_fields = (
        'name', 'cooking_time',
        'author__email', 'ingredients__name')
    list_filter = ('pub_date', 'tags',)

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return obj.favorite_recipe.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit',)
    search_fields = (
        'name', 'measurement_unit',)
    empty_value_display = '-пусто-'

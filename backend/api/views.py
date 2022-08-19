from rest_framework import generics, viewsets

from api.serializers import TagSerializer, IngredientSerializer, RecipeSerializer
from recipes.models import Tag, Ingredient, Recipe


class TagViewSet(viewsets.ViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

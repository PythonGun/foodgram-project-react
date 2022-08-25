from api.serializers import (IngredientSerializer, RecipeDetailSerializer,
                             RecipeFavoriteOrShoppingSerializer,
                             RecipeListSerializer, TagSerializer)
from django.shortcuts import get_object_or_404
from recipes.models import Favorite, Ingredient, Recipe, Tag
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from .permissions import IsAuthorOrAdminPermission


class TagViewSet(viewsets.ViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)    
    pagination_class = None


class RecipeViewSet(viewsets.ViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminPermission,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeDetailSerializer
    

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeFavoriteOrShoppingSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
            

        
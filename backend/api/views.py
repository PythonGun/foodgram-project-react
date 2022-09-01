from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (CustomUserSerializer, FollowSerializer,
                             IngredientSerializer, RecipeDetailSerializer,
                             RecipeFavoriteOrShoppingSerializer,
                             RecipeListSerializer, TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from users.models import Follow, User

from .filters import RecipeFilter
from .pagination import StandardPageNumberPagination
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
    pagination_class = StandardPageNumberPagination
    filter_class = RecipeFilter
    
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

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk):
        target_pk = self.kwargs.get('pk')
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=target_pk)

        if self.request.method == 'POST':
            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = RecipeFavoriteOrShoppingSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif self.request.method == 'DELETE':
            shopping_cart = get_object_or_404(
                ShoppingList,
                user=user,
                recipe=recipe
            )
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy_ingredient_list = RecipeIngredient.objects.filter(
            recipe__in=recipes
        ).values('ingredient').annotate(amount=Sum('amount'))

        shopping_list = 'Список покупок для рецептов:\n'
        for item in buy_ingredient_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            shopping_list += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )

        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )

        return response

class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            paginated_queryset, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete')
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            if request.user.id == author.id:
                raise ValidationError(
                    'Нельзя подписаться на себя'
                )
            else:
                serializer = FollowSerializer(
                    Follow.objects.create(user=request.user, author=author),
                    context={'request': request},
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )

        if request.method == 'DELETE':
            if Follow.objects.filter(
                    user=request.user, author=author
            ).exists():
                Follow.objects.filter(
                    user=request.user, author=author
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': 'В списке подписок нет такого автора'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

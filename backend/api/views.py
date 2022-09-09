from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models.expressions import Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User

from .filters import RecipeFilter, IngredientFilter
from .pagination import StandardPageNumberPagination
from .permissions import IsAuthorOrAdminPermission
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeDetailSerializer,
                          RecipeFavoriteOrShoppingSerializer,
                          RecipeListSerializer, TagSerializer, UserSerializer)
from .utils import create_delete_object


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminPermission,)
    pagination_class = StandardPageNumberPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeDetailSerializer

    def get_queryset(self):
        active_queryset = Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'tags',
            'ingredients',
            'recipe',
            'shopping_cart_recipe',
            'favorite_recipe',
        )
        if self.request.user.is_authenticated:
            active_queryset = active_queryset.annotate(
                is_favorited=Exists(
                    FavoriteRecipe.objects.filter(
                        user=self.request.user, recipe=OuterRef('id')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=self.request.user, recipe=OuterRef('id')
                    )
                ),
            )
        return active_queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return create_delete_object(
            request,
            pk,
            FavoriteRecipe,
            RecipeFavoriteOrShoppingSerializer
        )

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk):
        return create_delete_object(
            request,
            pk,
            ShoppingCart,
            RecipeFavoriteOrShoppingSerializer
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients_buy = RecipeIngredient.objects.filter(
            recipe__shopping_cart_recipe__user=request.user
        ).order_by(
            'ingredient__name'
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(ingredient_all_amount=Sum('amount'))

        buy_list_text = 'Список покупок с сайта Foodgram:\n\n'
        for item in ingredients_buy:
            buy_list_text += (
                f'{item["ingredient__name"]} - '
                f'{item["ingredient_all_amount"]} '
                f'{item["ingredient__measurement_unit"]}\n'
            )

        response = HttpResponse(buy_list_text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        serializer_class=FollowSerializer
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        serializer_class=FollowSerializer
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user.id == author.id:
                return ValidationError(
                    'Вы не можете подписаться на свой аккаунт'
                )
            else:
                serializer = self.get_serializer(
                    Follow.objects.create(user=request.user, author=author),
                    context={'request': request},
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            followed_user = get_object_or_404(
                Follow, user=user, author=author
            )
            followed_user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

from django.core.validators import MinValueValidator
from drf_base64.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import exceptions, serializers
from users.models import Follow, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', ' slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name',
            'last_name', 'email', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(user=user, author=obj).exists()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit',)


class CreateUpdateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=(MinValueValidator(1, messages='Ингредиент не может отсутсвовать'),)
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True,source='recipe')

    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text',   'cooking_time',
        )


class RecipeDetailSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredient = CreateUpdateRecipeIngredientSerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(
            1, message='Время приготовления не может быть меньше 1 минуты.'
        ),)
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate_tags(self, data):
        if not data:
            raise exceptions.ValidationError(
                'Нужно добавить хотя бы один тэг.'
            )
        return data

    def validate_ingredients(self, data):
        if not data:
            raise exceptions.ValidationError(
                'Нужно добавить хотя бы один ингредиент.'
            )
        ingredients = data['ingredients']
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise exceptions.ValidationError(
                    'В списке ингредиентов имеются одинаковые значения.'
                    'У рецепта не может быть два одинаковых ингредиента.'
                )
        return data

    def create_recipe_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient.get("id"),
                amount=ingredient.get("amount"),
            )

    def create(self, validated_data):
        author = self.context.get('author').user
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_recipe_ingredients(ingredients, recipe)
        return recipe

    def update(self, obj, validated_data):
        if "ingredients" in validated_data:
            ingredients = validated_data.pop("ingredients")
            obj.ingredients.clear()
            self.create_recipe_ingredients(ingredients, obj)
        if "tags" in validated_data:
            tags = validated_data.pop("tags")
            obj.tags.set(tags)
        return super().update(obj, validated_data)

    def to_representation(self, instance):
        serializer = RecipeListSerializer(instance)
        return serializer.data


class RecipeFavoriteOrShoppingSerializer(serializers.ModelField):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

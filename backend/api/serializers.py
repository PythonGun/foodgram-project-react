from django.core.validators import MinValueValidator
from drf_base64.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import exceptions, serializers
from users.models import Follow, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',  'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(user=user, author=obj).exists()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount',
        )


class CreateUpdateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe'
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )


class RecipeDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = CreateUpdateRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()
    
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
    
    def validate(self, data):
        tags = data['tags']
        if not tags:
            return exceptions.ValidationError(
                'Нужно добавить хотя бы один тэг.'
            )                   
    
        ingredients_recipe = data["ingredients"]
        ingredients_id = [item['id'] for item in ingredients_recipe]
        for ingredient in ingredients_id:
            if ingredients_id.count(ingredient) > 1:
                raise exceptions.ValidationError(
                    'У рецепта не может быть два одинаковых ингредиента.'
                )
        return data

    def create_recipe_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create([RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount']
        ) for ingredient in ingredients])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.create_recipe_ingredients(ingredients, recipe)
        return recipe

    def update(self, obj, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            obj.ingredients.clear()
            self.create_recipe_ingredients(ingredients, obj)
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            obj.tags.set(tags)
        return super().update(obj, validated_data)

    def to_representation(self, instance):
        serializer = RecipeListSerializer(instance)
        return serializer.data


class RecipeFavoriteOrShoppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author).order_by(
            '-pub_date'
        )
        return RecipeFavoriteOrShoppingSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
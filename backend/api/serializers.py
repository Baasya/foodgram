from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.models import CustomUser, Subscription

from . import constants as con
from .fields import Base64ImageField


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с аватаром."""
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = CustomUser
        fields = ('avatar',)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для информации о пользователях."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(allow_null=True, required=False)

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов рецептов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецептах."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецептах."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = RecipeIngredientSerializer(
        source='ingredient_list', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def check_model_object(self, obj, model):
        request = self.context.get('request')
        user = request.user
        return bool(
            request
            and user.is_authenticated
            and model.objects.filter(
                recipe=obj,
                user=user
            ).exists()
        )

    def get_is_favorited(self, obj):
        return self.check_model_object(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.check_model_object(obj, ShoppingCart)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецептов."""
    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_image(self, value):
        if not value:
            raise ValidationError('Добавьте изображение к рецепту')
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError('Укажите хотя бы один тэг')
        if len(value) != len(set(value)):
            raise ValidationError('Теги не должны повторяться')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Укажите хотя бы один ингредиент')
        ingredients_id = []
        for ingredient in value:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_id:
                raise ValidationError('Ингредиент уже добавлен')
            ingredients_id.append(ingredient_id)
        real_ingredients_number = Ingredient.objects.filter(
            id__in=ingredients_id).count()
        if real_ingredients_number != len(ingredients_id):
            raise ValidationError('Вы добавили несуществующие ингредиенты')
        return value

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    def create_recipe_tag(self, tags, recipe):
        recipe.tags.set(tags)

    def create_recipe_ingredient(self, ingredients, recipe):
        recipe_ingredients = []
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            one_ingredient = RecipeIngredient(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )
            recipe_ingredients.append(one_ingredient)
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=user,
            **validated_data
        )
        self.create_recipe_tag(tags, recipe)
        self.create_recipe_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.get('ingredients')
        if ingredients is None:
            raise ValidationError({'ingredients': 'Добавьте ингридиенты'})
        tags = validated_data.get('tags')
        if tags is None:
            raise ValidationError({'tags': 'Добавьте тег'})
        RecipeTag.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_recipe_tag(tags, instance)
        self.create_recipe_ingredient(ingredients, instance)
        return super().update(instance, validated_data)


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Упрощённый сериализатор для рецептов."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriberDetailSerializer (serializers.ModelSerializer):
    """Сериализатор для информации о подписках."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(source='author.avatar')

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        return Subscription.objects.filter(
            author=obj.author,
            user=user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if 'recipes_limit' in request.GET:
            limit = int(request.GET.get('recipes_limit'))
        else:
            limit = con.PAGE_SIZE
        return RecipeSmallSerializer(
            Recipe.objects.filter(author=obj.author)[:limit],
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class SubscriptionSerializer (serializers.ModelSerializer):
    """Сериализатор для подписки."""

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'author')

    def to_representation(self, instance):
        return SubscriberDetailSerializer(
            instance,
            context=self.context
        ).data

    def validate(self, value):
        request = self.context.get('request')
        user = request.user

        if user == value:
            raise serializers.ValidationError(con.SUBSCRIBE_ER_MESSAGE)
        if user.following.exists():
            raise serializers.ValidationError(con.SUBSCRIBE_EXIST_ER_MESSAGE)
        return value


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

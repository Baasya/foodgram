from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.models import CustomUser, Subscription

import constants as con
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
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
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
    """Сериализатор для .ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeWriteSerializer(serializers.ModelSerializer):

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


class RecipeSmallSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubsciberDetailSerializer (serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    avatar = Base64ImageField(source='author.avatar')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_amount = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_amount',
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

    def get_recipes_amount(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class SubscriptionSerializer (serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author')

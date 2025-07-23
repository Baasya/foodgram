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
            """Определяем значение поля is_subscribed."""
            request = self.context.get('request')
            if request is None or request.user.is_anonymous:
                return False
            return Subscription.objects.filter(
                user=request.user,
                author=obj).exists()
        # request.user.follower.filter(author=obj).exists()


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


class SubscriptionSerializer (serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author')

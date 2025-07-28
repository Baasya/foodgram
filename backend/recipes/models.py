from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from api.constants import (
    COOKING_TIME_MAX_MESSAGE,
    COOKING_TIME_MIN_MESSAGE,
    COOKING_TIME_MAX_VALUE,
    COOKING_TIME_MIN_VALUE,
    INGREDIENTS_AMOUNT_ERROR_MESSAGE,
    INGREDIENT_NAME_MAX_LENGTH,
    INGREDIENTS_MIN_AMOUNT,
    MEASUREMENT_UNIT_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    SLUG_ERROR_MESSAGE,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH
)
from users.models import User


class Tag(models.Model):
    """Модель для представления тэгов."""

    name = models.CharField(
        verbose_name='Тэг',
        max_length=TAG_NAME_MAX_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Slug тэга',
        unique=True,
        max_length=TAG_SLUG_MAX_LENGTH,
        validators=[RegexValidator(
            r'^[-a-zA-Z0-9_]+$',
            message=SLUG_ERROR_MESSAGE
        ),
        ]
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для представления ингредиентов."""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Еденица измерения',
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        blank=False
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['-id']
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.name}({self.measurement_unit})'


class Recipe(models.Model):
    """Модель для представления рецептов."""

    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=RECIPE_NAME_MAX_LENGTH
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки в минутах',
        validators=[
            MinValueValidator(
                COOKING_TIME_MIN_VALUE,
                message=COOKING_TIME_MIN_MESSAGE),
            MaxValueValidator(
                COOKING_TIME_MAX_VALUE,
                message=COOKING_TIME_MAX_MESSAGE),
        ]
    )
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='media/recipies/'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги рецепта',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты рецепта',
        related_name='recipes',
        through='RecipeIngredient'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи рецептов и ингредиентов."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredient_list',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredient_recipe',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                INGREDIENTS_MIN_AMOUNT,
                message=INGREDIENTS_AMOUNT_ERROR_MESSAGE),
        ]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} в составе {self.recipe}'


class Favorite(models.Model):
    """Модель для избранных рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        related_name='favorite',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Избранное пользователя',
        related_name='favorite',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'избранный'
        verbose_name_plural = 'Избранное'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.recipe}'


class ShoppingCart(models.Model):
    """Модель для корзины покупок."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_cart_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.recipe}'

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from api import constants as con
from users.models import CustomUser


class Tag(models.Model):
    """Модель для представления тэгов."""

    name = models.CharField(
        verbose_name='Тэг',
        max_length=con.TAG_NAME_MAX_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Slug тэга',
        unique=True,
        max_length=con.TAG_SLUG_MAX_LENGTH,
        validators=[RegexValidator(
            r'^[-a-zA-Z0-9_]+$',
            message=con.SLUG_ERROR_MESSAGE
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
        max_length=con.INGREDIENT_NAME_MAX_LENGTH,
        blank=False,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Еденица измерения',
        max_length=con.MEASUREMENT_UNIT_MAX_LENGTH,
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
        blank=False,
        max_length=con.RECIPE_NAME_MAX_LENGTH
    )
    text = models.TextField(
        verbose_name='Описание',
        blank=False,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки в минутах',
        validators=[
            MinValueValidator(
                con.COOKING_TIME_MIN_VALUE,
                message=con.COOKING_TIME_ERROR_MESSAGE),
        ]
    )
    image = models.ImageField(
        verbose_name='Фото блюда',
        blank=False,
        upload_to='media/recipies/'
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги рецепта',
        related_name='recipes',
        blank=False,
        through='RecipeTag'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты рецепта',
        related_name='recipes',
        blank=False,
        through='RecipeIngredient'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Промежуточная модель для связи рецептов и тэгов."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='tag_list',
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тэг',
        related_name='tag_recipe',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'тэг рецепта'
        verbose_name_plural = 'Тэги рецепта'
        ordering = ['-id']

    def __str__(self):
        return f'Тэг рецепта {self.recipe} - {self.tag}.'


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
                con.INGREDIENTS_MIN_AMOUNT,
                message=con.INGREDIENTS_AMOUNT_ERROR_MESSAGE),
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
        CustomUser,
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
        CustomUser,
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

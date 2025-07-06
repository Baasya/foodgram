from django.core.validators import (MinValueValidator, RegexValidator)
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


class Ingridients(models.Model):
    """Модель для представления ингридиентов."""

    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=con.INGREDIENT_NAME_MAX_LENGTH,
        blank=False,
    )
    measurement_unit = models.CharField(
        verbose_name='Еденица измерения',
        max_length=con.MEASUREMENT_UNIT_MAX_LENGTH,
        blank=False
    )

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}({self.measurement_unit})'


class Recipe(models.Model):
    """Модель для представления рецептов."""

    name = models.CharField(
        verbose_name='Название рецепта',
        blanke=False,
        max_length=con.RECIPE_NAME_MAX_LENGTH
    )
    text = models.TextField(
        verbose_name='Описание',
        blanke=False,
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
        blanke=False,
        upload_to='media/recipies/'
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    # ingridients - Many to Many
    # tags - Many to Many

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name

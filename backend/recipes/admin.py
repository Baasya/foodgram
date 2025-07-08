from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag


class RecipeTagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки панели администрирования ингридиентов."""
    fields = ('name', 'measurement_unit')
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('id', 'name')
    list_per_page = 20
    search_fields = ('name', )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки панели администрирования рецептов."""
    fields = ('name', 'author', 'cooking_time', 'image', 'text')
    list_display = ('id', 'name', 'author', 'count_favorite')
    list_display_links = ('id', 'name')
    inlines = [RecipeTagInline, RecipeIngredientInline]
    list_filter = ('tags', )
    search_fields = ('name', 'author')
    empty_value_display = '-пусто-'

    @admin.display(description='В избранном у')
    def count_favorite(self, obj):
        return obj.favorite.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки панели администрирования тэгов."""
    fields = ('name', 'slug')
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    empty_value_display = '-пусто-'

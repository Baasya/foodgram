from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Настройки панели администрирования пользователями."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('username', 'first_name', 'last_name', 'email')
    search_fields = ('email', 'first_name')
    ordering = ('username', )
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройки панели администрирования подписками."""

    list_display = (
        'id',
        'user',
        'author',
    )
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')
    ordering = ('user', )
    empty_value_display = '-пусто-'

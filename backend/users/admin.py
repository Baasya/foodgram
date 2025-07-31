from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.models import Subscription

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройки панели администрирования пользователями."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_display_links = ('id', 'username')
    list_filter = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'username')
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
    list_display_links = ('id', 'user')
    list_filter = ('user', )
    search_fields = ('user', )
    ordering = ('user', )
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = Subscription.objects.select_related('user')
        return queryset

from django.db.models import Sum
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.models import CustomUser, Subscription

# import constants as con
from .filter import IngredientFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (AvatarSerializer, CustomUserSerializer,
                          CustomUserCreateSerializer,
                          IngredientSerializer,
                          TagSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer)


class CustomUserViewSet(UserViewSet):
    """Представление для пользователей."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        """Получение профиля пользователя."""
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    @action(
        methods=['put'],
        detail=False,
        permission_classes=(IsAdminOrAuthorOrReadOnly,),
        url_path='me/avatar',
        url_name='me/avatar',
    )
    def avatar(self, request, *args, **kwargs):
        """Добавдение фото профиля."""
        serializer = AvatarSerializer(
            instance=request.user,
            data=request.data,
        )
        # выкинет ошибку 400 
        serializer.is_valid(raise_exeption=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        """Удаление фото профиля."""
        user = self.request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class через метод
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

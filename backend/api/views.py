from io import BytesIO

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

from .filter import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (AvatarSerializer, CustomUserCreateSerializer,
                          CustomUserSerializer, FavoriteRecipeSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeSmallSerializer, RecipeWriteSerializer,
                          ShoppingCartCreateSerializer,
                          SubscriberDetailSerializer, SubscriptionSerializer,
                          TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Представление для пользователей."""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(
        methods=['post'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request, *args, **kwargs):
        user = self.request.user
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response(
                'Пароль изменён', status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
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
        serializer = AvatarSerializer(
            instance=request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        user = self.request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
        url_name='subscriptions',
    )
    def subscriptions(self, request):
        user = request.user
        queryset = user.follower.annotate(
            recipe_count=Count('author__recipes'))
        pages = self.paginate_queryset(queryset)
        serializer = SubscriberDetailSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = request.user
        if self.request.method == 'POST':
            author = get_object_or_404(User, id=id)
            data = {'user': user.id, 'author': author.id}
            serializer = SubscriptionSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            queryset = (
                user.follower
                .annotate(recipes_count=Count('author__recipes'))
            ).first()
            serializer = SubscriberDetailSerializer(
                queryset, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif self.request.method == 'DELETE':
            user = get_object_or_404(User, id=request.user.id)
            deleted_count, _ = user.following.filter(
                user=user, author_id=id
            ).delete()
            if deleted_count == 0:
                return Response(
                    {"detail": 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
    """Представление для рецептов."""

    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'ingredients'
    )
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'get-link'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        methods=['get'],
        detail=True,
        permission_classes=(AllowAny,),
        url_path='get-link',
        url_name='get-link',
    )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        reverse_link = reverse('short_url', args=[recipe.pk])
        return Response(
            {'short-link': request.build_absolute_uri(reverse_link)},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            data = {'user': user.id, 'recipe': recipe.id}
            serializer = ShoppingCartCreateSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = RecipeSmallSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            deleted_count, _ = user.shopping_cart.filter(
                user=user, recipe=recipe
            ).delete()
            if deleted_count == 0:
                return Response(
                    {"detail": f'{recipe} не в корзине покупок.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def buffer_for_shopping_file(user):
        ingredients = (
            RecipeIngredient.objects.filter(recipe__shopping_cart__user=user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit'
            )
            .annotate(total_amount=Sum('amount'))
        )
        buffer = BytesIO()
        for ingredient in ingredients:
            ingredient_name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            total_amount = ingredient['total_amount']
            buffer.write(
                f'{ingredient_name} - ({measurement_unit})'
                f'— {total_amount} \n'.encode('utf-8'))
        buffer.seek(0)
        return buffer

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = request.user
        buffer = self.buffer_for_shopping_file(user)
        return FileResponse(
            buffer,
            as_attachment=True,
            content_type='text/plain',
            filename='shopping_cart.txt'
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            data = {'user': user.id, 'recipe': recipe.id}
            serializer = FavoriteRecipeSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = RecipeSmallSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            deleted_count, _ = user.favorite.filter(
                user=user, recipe=recipe
            ).delete()
            if deleted_count == 0:
                return Response(
                    {"detail": f'{recipe} не в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(status=status.HTTP_204_NO_CONTENT)


@require_GET
def short_url(request, pk):
    return redirect(f'/recipes/{pk}/')

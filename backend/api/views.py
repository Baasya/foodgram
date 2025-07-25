from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import CustomUser, Subscription

from . import constants as con
from .filter import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (AvatarSerializer, CustomUserSerializer,
                          FavoriteRecipeSerializer, IngredientSerializer,
                          TagSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, SubscriberDetailSerializer,
                          SubscriptionSerializer)


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
        serializer.is_valid(raise_exeption=True)
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
        queryset = user.follower.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscriberDetailSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginate_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)

        if self.request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': con.SUBSCRIBE_ER_MESSAGE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': con.SUBSCRIBE_EXIST_ER_MESSAGE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = Subscription.objects.create(author=author, user=user)
            serializer = SubscriptionSerializer(
                queryset,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif self.request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=user, author=author
            ).exists():
                return Response(
                    {'errors': con.SUBSCRIBE_NOT_EXIST_ER_MESSAGE},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscription = get_object_or_404(
                Subscription, user=user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_205_NO_CONTENT)


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
        try:
            recipe = get_object_or_404(Recipe, pk=pk)
        except Recipe.DoesNotExist:
            raise NotFound('Не удалось найти рецепт.')
        else:
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
            if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
                return Response(
                    {'detail': f'{recipe.name} уже добавлен в корзину.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(recipe=recipe, user=user)
            serializer = FavoriteRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            cart_recipe = ShoppingCart.objects.filter(recipe__id=pk, user=user)
            if cart_recipe.exists():
                cart_recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'detail': f'{recipe.name} отсутствует в корзине.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects.filter(recipe__shopping_cart__user=user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit'
            )
            .annotate(total_amount=Sum('amount'))
        )

        response_text = ''
        for ingredient in ingredients:
            ingredient_name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            total_amount = ingredient['total_amount']
            response_text += (
                f'{ingredient_name} - ({measurement_unit})'
                f'— {total_amount} \n')

        response = HttpResponse(response_text, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
        return response

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
            if Favorite.objects.filter(recipe=recipe, user=user).exists():
                return Response(
                    {'detail': f'{recipe.name} уже в избанном.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favorite.objects.create(recipe=recipe, user=user)
            serializer = FavoriteRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            favorites = Favorite.objects.filter(recipe=recipe, user=user)
            if favorites.exists():
                favorites.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'detail': f'{recipe.name} отсутствует в избранном'},
                    status=status.HTTP_400_BAD_REQUEST,
                )


@require_GET
def short_url(request, pk):
    return redirect(f'/recipes/{pk}/')

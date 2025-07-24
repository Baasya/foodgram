from django.db.models import Count, Sum
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

import constants as con
from .filter import IngredientFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (AvatarSerializer, CustomUserSerializer,
                          IngredientSerializer,
                          TagSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer,
                          SubscriberDetailSerializer,
                          SubscriptionSerializer)                   

    # HTTP_200_OK,
    # HTTP_201_CREATED,
    # HTTP_204_NO_CONTENT,
    # HTTP_400_BAD_REQUEST,
    # HTTP_404_NOT_FOUND,


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
        # выкинет ошибку 400 
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
            if not Subscription.objects.filter(user=user, author=author).exists():
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
    # serializer_class через метод
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

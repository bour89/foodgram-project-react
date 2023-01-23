from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Follow, User

from . import serializers
from .filters import Filter
from .pagination import LimitPagination
from .permissions import IsAuthorOrAdminPermission


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Тэги"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializers
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)
    pagination_class = None


class ListSubscriptions(generics.ListAPIView):
    """Список покупок"""
    serializer_class = serializers.SubscriptionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты"""
    queryset = Recipe.objects.all()
    pagination_class = LimitPagination
    serializer_class = serializers.RecipePostSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = Filter

    def get_permissions(self):
        if self.action in ('update', 'destroy'):
            permission_classes = [IsAuthorOrAdminPermission]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.RecipeGetSerializer
        return serializers.RecipePostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        recipe = get_object_or_404(Recipe, pk=serializer.data.get('id'))
        new_serializer = serializers.RecipeGetSerializer(
            recipe,
            context={'request': request}
        )
        return Response(new_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        recipe = get_object_or_404(Recipe, pk=serializer.data.get('id'))
        new_serializer = serializers.RecipeGetSerializer(
            recipe,
            context={'request': request},
            partial=partial
        )
        return Response(new_serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, ),
    )
    def download_shopping_cart(self, request):
        ingredient_list = IngredientRecipe.objects.filter(
            recipe__recipe_cart__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(sum_amount=Sum('amount'))
        shopping_list = ['Cписок покупок:\n']
        shopping_list += '\n'.join([
            f'{ingredient["ingredient__name"]}'
            f'({ingredient["ingredient__measurement_unit"]}) - '
            f'{ingredient["sum_amount"]}'
            for ingredient in ingredient_list
        ])
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_shopping_cart = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if request.method == 'POST':
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = serializers.ShortRecipeSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            recipe_in_shopping_cart.delete()
            return Response(
                'Рецепт успешно удалён из списка покупок',
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = FavoriteRecipe.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if request.method == 'POST':
            FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
            serializer = serializers.ShortRecipeSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            recipe_in_favorite.delete()
            return Response('Рецепт успешно удалён из избранного',
                            status.HTTP_204_NO_CONTENT)


class Subscribe(APIView):
    """Подписка на пользователя/отписка от пользователя"""
    def get_permissions(self):
        permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        is_subscribed = Follow.objects.filter(user=request.user, author=author)
        if author == request.user:
            return Response("Нельзя подписаться на самого себя",
                            status=status.HTTP_400_BAD_REQUEST)
        elif is_subscribed.exists():
            return Response(
                "Вы уже подписались на этого автора.",
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            Follow.objects.create(user=request.user, author=author)
            serializer = serializers.IsSubscribeSerializer(
                author,
                context={'request': 'request'}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        subscription = Follow.objects.filter(user=request.user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response(
                'Вы успешно отписались от этого автора!',
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                'Вы ещё не подписаны на этого автора.',
                status.HTTP_400_BAD_REQUEST
            )

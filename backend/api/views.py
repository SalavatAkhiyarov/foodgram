import io

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import smart_str
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from foodgram.constants import DEFAULT_PAGE_SIZE
from foodgram.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                             ShoppingCart, Subscription, Tag)
from .filters import IngredientFilter, RecipeFilter
from .pagination import RecipePagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, SubscribeCreateSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserAvatarSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects
        .select_related('author')
        .prefetch_related('tags', 'recipe_ingredients__ingredient')
        .order_by('-pub_date')
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _add_to_relation(self, serializer_class, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {'user': self.request.user.id, 'recipe': recipe.id}
        serializer = serializer_class(
            data=data, context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from_relation(self, model, pk, not_found_error):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj, _ = model.objects.filter(
            user=self.request.user, recipe=recipe
        ).delete()
        if obj:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'errors': not_found_error}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self._add_to_relation(FavoriteSerializer, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self._remove_from_relation(
            Favorite, pk, 'Рецепта нет в избранном'
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return self._add_to_relation(ShoppingCartSerializer, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self._remove_from_relation(
            ShoppingCart, pk, 'Рецепта нет в корзине'
        )

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=(AllowAny,)
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        link = request.build_absolute_uri(
            reverse('short-link', args=[recipe.id])
        )
        return Response({'short-link': link})

    @staticmethod
    def _generate_shopping_list(user, ingredients):
        lines = [f'Список покупок для {user.username}\n']
        for i, item in enumerate(ingredients, 1):
            lines.append(
                f'{i}. {item["ingredient__name"]} — '
                f'{item["total_amount"]} '
                f'{item["ingredient__measurement_unit"]}'
            )
        return '\n'.join(lines)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_carts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        content = self._generate_shopping_list(user, ingredients)
        file_stream = io.BytesIO(content.encode('utf-8'))
        response = FileResponse(
            file_stream,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            f'attachment; filename={smart_str("shopping_list.txt")}'
        )
        return response


class AddUserViewSet(DjoserUserViewSet):
    lookup_field = 'pk'

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request):
        serializer = UserAvatarSerializer(
            request.user, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(
            User.objects.annotate(
                recipes_count=Count('recipes', distinct=True)
            ),
            pk=pk
        )
        data = {'user': request.user.id, 'author': author.id}
        serializer = SubscribeCreateSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        author_payload = SubscriptionSerializer(
            author, context={'request': request}
        ).data
        return Response(author_payload, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = get_object_or_404(
            User.objects.annotate(
                recipes_count=Count('recipes', distinct=True)
            ),
            pk=pk
        )
        obj, _ = Subscription.objects.filter(
            user=request.user, author=author
        ).delete()
        if obj:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не были подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            subscriptions_to_author__user=request.user
        ).annotate(
            recipes_count=Count('recipes', distinct=True)
        ).order_by('username')
        paginator = LimitOffsetPagination()
        paginator.default_limit = DEFAULT_PAGE_SIZE
        paginator.limit_query_param = 'limit'
        page = paginator.paginate_queryset(subscriptions, request, view=self)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            subscriptions, many=True, context={'request': request})
        return Response(serializer.data)

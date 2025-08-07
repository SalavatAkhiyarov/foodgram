from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)

from foodgram.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = NumberFilter(field_name='author__id')
    is_in_shopping_cart = BooleanFilter(method='filter_in_shopping_cart')
    is_favorited = BooleanFilter(method='filter_is_favorited')

    def filter_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset
        if value:
            return queryset.filter(in_shopping_carts__user=user)
        return queryset.exclude(in_shopping_carts__user=user)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset
        if value:
            return queryset.filter(favorited_by__user=user)
        return queryset.exclude(favorited_by__user=user)

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)

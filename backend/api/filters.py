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
    is_in_shopping_cart = BooleanFilter(method='filter_in_shopping_cart')
    is_favorited = BooleanFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')

    def filter_is_favorited(self, queryset, name, value):
        user_id = getattr(self.request.user, 'id', None)
        if value and user_id:
            return queryset.filter(favorited_by__user_id=user_id)
        if not value and user_id:
            return queryset.exclude(favorited_by__user_id=user_id)
        return queryset.none() if value else queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        user_id = getattr(self.request.user, 'id', None)
        if value and user_id:
            return queryset.filter(in_shopping_carts__user_id=user_id)
        if not value and user_id:
            return queryset.exclude(in_shopping_carts__user_id=user_id)
        return queryset.none() if value else queryset


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)

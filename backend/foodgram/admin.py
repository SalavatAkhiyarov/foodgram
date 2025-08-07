from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username')
    list_filter = ('username', 'email')
    ordering = ('id',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name',)

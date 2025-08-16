from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram.constants import (MAX_POSITIVE_SMALLINT, MIN_POSITIVE_SMALLINT,
                                RECIPE_NAME_MAX_LENGTH)
from foodgram.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                             ShoppingCart, Subscription, Tag, User)


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = DjoserUserSerializer.Meta.fields + ('avatar', 'is_subscribed')
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.subscriptions_to_author.filter(user=request.user).exists()
        )


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeWriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=MIN_POSITIVE_SMALLINT,
        max_value=MAX_POSITIVE_SMALLINT
    )


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    image = serializers.ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.shoppingcarts.filter(user=request.user).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=RECIPE_NAME_MAX_LENGTH)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(required=True, allow_null=False)
    cooking_time = serializers.IntegerField(
        min_value=MIN_POSITIVE_SMALLINT,
        max_value=MAX_POSITIVE_SMALLINT
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
        )

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Изображение обязательно')
        return value

    def validate(self, data):
        ingredient_list = data.get('ingredients')
        tag_list = data.get('tags')
        if not ingredient_list:
            raise serializers.ValidationError(
                {'ingredients': 'Добавьте хотя бы один ингредиент'}
            )
        if not tag_list:
            raise serializers.ValidationError(
                {'tags': 'Добавьте хотя бы один тег'}
            )
        ingredient_ids = [ingredient['id'] for ingredient in ingredient_list]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться'}
            )
        if len(tag_list) != len(set(tag_list)):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться'}
            )
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._set_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        self._set_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    @staticmethod
    def _set_ingredients(recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ])

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True, default=0)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context['request']
        recipes = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except (TypeError, ValueError):
                pass
        return ShortRecipeSerializer(
            recipes, many=True, context=self.context
        ).data


class SubscribeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        user = self.context['request'].user
        author = data['author']
        if user == author:
            raise serializers.ValidationError('Нельзя подписаться на себя')
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя'
            )
        data['user'] = user
        return data

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.author, context=self.context
        ).data


class RecipeRelationSerializer(serializers.ModelSerializer):

    class Meta:
        model = None
        fields = ('user', 'recipe')
        read_only_fields = ('user',)

    def validate(self, data):
        user = self.context['request'].user
        recipe = data['recipe']
        model = self.Meta.model
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': f'{model._meta.verbose_name} уже добавлен'}
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteSerializer(RecipeRelationSerializer):

    class Meta(RecipeRelationSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(RecipeRelationSerializer):

    class Meta(RecipeRelationSerializer.Meta):
        model = ShoppingCart

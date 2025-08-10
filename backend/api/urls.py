from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import djoser_extension  # noqa: F401
from . import views

router = DefaultRouter()
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('tags', views.TagViewSet, basename='tags')
router.register('ingredients', views.IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('s/<int:recipe_id>/', views.short_link_redirect, name='short_link')
]

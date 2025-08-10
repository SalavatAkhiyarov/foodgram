from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import djoser_permissons  # noqa: F401
from . import views

router = DefaultRouter()
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('tags', views.TagViewSet, basename='tags')
router.register('ingredients', views.IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(
        'users/me/avatar/',
        views.AddUserViewSet.as_view(
            {'put': 'avatar', 'delete': 'avatar'}
        )
    ),
    path(
        'users/<int:pk>/subscribe/',
        views.AddUserViewSet.as_view(
            {'post': 'subscribe', 'delete': 'subscribe'}
        )
    ),
    path(
        'users/subscriptions/',
        views.AddUserViewSet.as_view(
            {'get': 'subscriptions'}
        )
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]

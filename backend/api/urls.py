from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, ListSubscriptions, RecipeViewSet,
                    Subscribe, TagViewSet)

router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('users/subscriptions/', ListSubscriptions.as_view()),
    path('users/<int:pk>/subscribe/', Subscribe.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

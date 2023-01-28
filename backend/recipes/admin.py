from django.contrib import admin

from . import models


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author__username', 'author__email', 'name')


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )


admin.site.register(models.ShoppingCart)
admin.site.register(models.Tag)
admin.site.register(models.IngredientRecipe)
admin.site.register(models.FavoriteRecipe)

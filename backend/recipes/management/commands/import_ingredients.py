import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        filepath = os.path.join(
            settings.BASE_DIR, '..', 'data', 'ingredients.json'
        )

        with open(filepath, encoding='utf-8') as ingredients_file:
            ingredients = json.load(ingredients_file)
            for ingredient in ingredients:
                obj, _ = models.Ingredient.objects.get_or_create(**ingredient)
                self.stdout.write(f'Loaded "{obj}"')

        self.stdout.write(
            self.style.SUCCESS(
                'Database has been filled successfully!'
            )
        )

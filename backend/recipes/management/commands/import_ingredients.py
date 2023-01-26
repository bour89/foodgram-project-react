import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из csv файла'

    def handle(self, *args, **kwargs):
        filename = path.join('.', 'data', 'ingredients.csv')
        try:
            with open(filename, 'r', encoding='UTF-8') as file:
                for row in csv.reader(file):
                    Ingredient.objects.get_or_create(
                        name=row[0], measurement_unit=row[1],
                    )
            self.stdout.write(self.style.SUCCESS('Ингридиенты импортированы'))
        except Exception:
            self.stdout.write(self.style.ERROR('Ошибка импорта ингридентов'))

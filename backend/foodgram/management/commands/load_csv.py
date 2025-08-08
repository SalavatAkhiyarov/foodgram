import os
import csv

from django.core.management.base import BaseCommand
from django.conf import settings
from foodgram.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из backend/data/ingredients.csv'

    def handle(self, *args, **kwargs):
        data_path = os.path.join(settings.BASE_DIR, 'data')
        file_path = os.path.join(data_path, 'ingredients.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
            return
        with open(file_path, encoding='utf-8') as f:
            reader = csv.reader(f)
            ingredients = []
            for row in reader:
                if len(row) != 2:
                    self.stdout.write(self.style.WARNING(f'Пропущена строка: {row}'))
                    continue
                name, unit = row[0].strip(), row[1].strip()
                if name and unit:
                    ingredients.append(Ingredient(name=name, measurement_unit=unit))
        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Загружено {len(ingredients)} ингредиентов'))

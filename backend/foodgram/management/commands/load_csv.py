import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

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
            ingredients_to_add = []
            existing = set(
                (name.lower(), unit.lower())
                for name, unit in Ingredient.objects.values_list(
                    'name', 'measurement_unit'
                )
            )
            for row in reader:
                if len(row) != 2:
                    self.stdout.write(
                        self.style.WARNING(f'Пропущена строка: {row}')
                    )
                    continue
                name, unit = row[0].strip(), row[1].strip()
                if (
                    name
                    and unit
                    and (name.lower(), unit.lower()) not in existing
                ):
                    ingredients_to_add.append(
                        Ingredient(name=name, measurement_unit=unit)
                    )
        if ingredients_to_add:
            Ingredient.objects.bulk_create(ingredients_to_add)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Загружено {len(ingredients_to_add)} ингредиентов'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('Новых ингредиентов не найдено')
            )

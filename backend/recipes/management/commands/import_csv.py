import csv

from django.core.management import BaseCommand

from foodgram import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для очистки базы данных и загрузки csv файла."""

    help = (
        'Команда для импорта данных в модель Ingredients. '
        'Синтаксис команды: python manage.py import_csv /путь к файлу/. '
    )

    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs=1, type=str)

    def handle(self, *args, **options):
        file_path = f'{settings.BASE_DIR}/data/ingredients.csv'
        Ingredient.objects.all().delete()
        items_list = []
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                model_item = Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
                items_list.append(model_item)
            Ingredient.objects.bulk_create(items_list)
            self.stdout.write('==== Успешный импорт в модель Ingredient ====')

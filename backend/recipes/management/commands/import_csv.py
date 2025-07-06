import csv

from django.core.management import BaseCommand

from foodgram import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для очистки базы данных и загрузки csv файла."""

    help = (
        'Команда для импорта данных в модель Ingredients. '
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
                name_index = 0
                unit_index = 1
                model_item = Ingredient(
                    name=row[name_index],
                    measurement_unit=row[unit_index],
                )
                items_list.append(model_item)
            Ingredient.objects.bulk_create(items_list)
            self.stdout.write('======   Успешный импорт в модель Ingredient   ======')

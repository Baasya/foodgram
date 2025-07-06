from csv import DictReader

from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для очистки базы данных и загрузки csv файла."""

    help = (
        'Команда для импорта данных в модель Ingredients. '
    )

    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs=1, type=str)

    def handle(self, *args, **options):
        file_path = options['file_path'][0]
        Ingredient.objects.all().delete()
        items_list = []
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = DictReader(f)
            for row in reader:
                model_item = Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
                items_list.append(model_item)
            Ingredient.objects.bulk_create(items_list)
            self.stdout.write('======   Успешный мпорт csv файла   ======')

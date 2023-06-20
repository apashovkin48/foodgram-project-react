from django.core.management.base import BaseCommand
from core.utils import load_table_from_json
from recipes.models import Ingredient


class Command(BaseCommand):
    """
    This command import static data.
    Example: Ingredient, ... from JSON file
    """
    def handle(self, *args, **options):
        self.stdout.write('Start loading static data from json files')
        load_table_from_json(Ingredient, 'ingredients')
        self.stdout.write('Load static data success')

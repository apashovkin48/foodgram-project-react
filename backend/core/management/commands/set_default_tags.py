from django.core.management.base import BaseCommand
from core.utils import load_table_from_json
from recipes.models import Tag


class Command(BaseCommand):
    """
    This command import static data.
    Example: Tags, ... from JSON file
    """
    def handle(self, *args, **options):
        self.stdout.write('Start loading static data from json files')
        load_table_from_json(Tag, 'tags')
        self.stdout.write('Load static data success')

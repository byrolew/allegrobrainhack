from django.core.management.base import BaseCommand, CommandError
from core.utils import load_keywords

class Command(BaseCommand):
    help = 'Load keywords'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str)

    def handle(self, *args, **options):
        load_keywords(options['file'])


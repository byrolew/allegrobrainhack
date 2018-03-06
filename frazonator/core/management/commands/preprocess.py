from django.core.management.base import BaseCommand, CommandError
from core.utils import preprocess

class Command(BaseCommand):
    help = 'preprocess'

    def handle(self, *args, **options):
        preprocess()

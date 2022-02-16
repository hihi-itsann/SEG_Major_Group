from django.core.management.base import BaseCommand, CommandError

from bookclubs.models import User
from bookclubs.models import Post

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        User.objects.filter(is_staff=False).delete()

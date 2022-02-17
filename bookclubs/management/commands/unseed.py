from django.core.management.base import BaseCommand, CommandError

from bookclubs.models import User, Club

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        Club.objects.all().delete()
        User.objects.filter(is_staff=False).delete()

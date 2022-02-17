from django.core.management.base import BaseCommand, CommandError

from bookclubs.models import User, Club, Role

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        Role.objects.all().delete()
        Club.objects.all().delete()
        User.objects.filter(is_staff=False).delete()

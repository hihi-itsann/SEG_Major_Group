from django.core.management.base import BaseCommand, CommandError

from bookclubs.models import User, Post, Comment, Club, Role, Book, Rating, Meeting

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        Meeting.objects.all().delete()
        Rating.objects.all().delete()
        Book.objects.all().delete()
        Role.objects.all().delete()
        Club.objects.all().delete()
        Comment.objects.all().delete()
        Post.objects.all().delete()
        User.objects.filter(is_staff=False).delete()

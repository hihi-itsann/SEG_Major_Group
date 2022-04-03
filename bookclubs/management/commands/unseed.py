from django.core.management.base import BaseCommand

from bookclubs.meeting_link import delete_zoom_meeting
from bookclubs.models import User, Post, Comment, Club, Role, Book, BookRatingReview, Meeting, ClubBookAverageRating, \
    MeetingAttendance, Application


class Command(BaseCommand):
    help = 'Empties the database'

    def handle(self, *args, **options):
        print(f'Unseeding started...', end='\r')
        if ClubBookAverageRating.objects.all().count() > 0:
            print(f'Unseeding ClubBookAverageRating...', end='\r')
            ClubBookAverageRating.objects.all().delete()
            print(f'Unseeded ClubBookAverageRating.')
        if MeetingAttendance.objects.all().count() > 0:
            print(f'Unseeding MeetingAttendance...', end='\r')
            MeetingAttendance.objects.all().delete()
            print(f'Unseeded MeetingAttendance.')
        if Meeting.objects.all().count() > 0:
            print(f'Unseeding Meeting...', end='\r')
            Meeting.objects.all().delete()
            delete_zoom_meeting()
            print(f'Unseeded Meeting.')
        if Comment.objects.all().count() > 0:
            print(f'Unseeding Comment...', end='\r')
            Comment.objects.all().delete()
            print(f'Unseeded Comment.')
        if Post.objects.all().count() > 0:
            print(f'Unseeding Post...', end='\r')
            Post.objects.all().delete()
            print(f'Unseeded Post.')
        if Application.objects.all().count() > 0:
            print(f'Unseeding Application...', end='\r')
            Application.objects.all().delete()
            print(f'Unseeded Application.')
        if Role.objects.all().count() > 0:
            print(f'Unseeding Role...', end='\r')
            Role.objects.all().delete()
            print(f'Unseeded Role.')
        if Club.objects.all().count() > 0:
            print(f'Unseeding Club...', end='\r')
            Club.objects.all().delete()
            print(f'Unseeded Club.')
        if BookRatingReview.objects.all().count() > 0:
            print(f'Unseeding Rating...', end='\r')
            BookRatingReview.objects.all().delete()
            print(f'Unseeded Rating.')
        if User.objects.filter(is_staff=False).count() > 0:
            print(f'Unseeding User...', end='\r')
            User.objects.filter(is_staff=False).delete()
            print(f'Unseeded User.')
        if Book.objects.all().count() > 0:
            print(f'Unseeding Book...', end='\r')
            Book.objects.all().delete()
            print(f'Unseeded Book.')
        print('Unseeding finished.')

from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Club, Meeting, Book

# TODO: Finish this.
class MeetingModelTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_clubs.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(club_name='private_online')
        self.book = Book.objects.get(ISBN='0195153448')
        self.meeting = Meeting.objects.create(
            club=self.club,
            book=self.book,
            topic='[Topic]',
            description='[Description]',
            meeting_status='ONL'
        )


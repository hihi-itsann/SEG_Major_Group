from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Club, Meeting, Book, MeetingAttendance

# TODO: Finish this.
class MeetingModelTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.book = Book.objects.get(ISBN='0195153448')
        self.meeting = Meeting.objects.create(
            club=self.club,
            book=self.book,
            topic='[Topic]',
            description='[Description]',
            meeting_status='ONL',
            location='Bush House',
            date='2022-04-01',
            time_start='11:00',
            time_end='13:00'
        )

    def test_is_attending(self):
        host = MeetingAttendance.objects.create(user=self.user, meeting=self.meeting, meeting_role='H')
        self.assertTrue(self.meeting.is_attending(self.user))
        host.delete()
        self.assertFalse(self.meeting.is_attending(self.user))
        attendee = MeetingAttendance.objects.create(user=self.user, meeting=self.meeting, meeting_role='A')
        self.assertTrue(self.meeting.is_attending(self.user))
        attendee.delete()
        self.assertFalse(self.meeting.is_attending(self.user))






from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Club, Meeting, Book, MeetingAttendance


class MeetingModelTestCase(TestCase):
    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
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

    def test_is_host(self):
        host = MeetingAttendance.objects.create(user=self.user, meeting=self.meeting, meeting_role='H')
        self.assertTrue(self.meeting.is_host(self.user))
        host.delete()
        self.assertFalse(self.meeting.is_host(self.user))
        attendee = MeetingAttendance.objects.create(user=self.user, meeting=self.meeting, meeting_role='A')
        self.assertFalse(self.meeting.is_host(self.user))
        attendee.delete()
        self.assertFalse(self.meeting.is_host(self.user))

    def test_is_attendee_only(self):
        host = MeetingAttendance.objects.create(user=self.user, meeting=self.meeting, meeting_role='H')
        self.assertFalse(self.meeting.is_attendee_only(self.user))
        host.delete()
        self.assertFalse(self.meeting.is_attendee_only(self.user))
        attendee = MeetingAttendance.objects.create(user=self.user, meeting=self.meeting, meeting_role='A')
        self.assertTrue(self.meeting.is_attendee_only(self.user))
        attendee.delete()
        self.assertFalse(self.meeting.is_attendee_only(self.user))

    def test_get_host(self):
        user_two = User.objects.get(username='@janedoe')
        MeetingAttendance.objects.create(user=self.user, meeting=self.meeting, meeting_role='H')
        attendee = MeetingAttendance.objects.create(user=user_two, meeting=self.meeting, meeting_role='A')
        self.assertEqual(self.meeting.get_host(), self.user)
        self.assertNotEqual(self.meeting.get_host(), attendee)

    def test_get_meeting_status(self):
        self.assertEqual(self.meeting.get_meeting_status(), 'Online')
        self.meeting.meeting_status = 'OFF'
        self.assertEqual(self.meeting.get_meeting_status(), 'In-Person')

    def test_get_location(self):
        self.assertTrue(self.meeting.get_location().__contains__('Meeting Link:'))
        self.meeting.meeting_status = 'OFF'
        self.assertTrue(self.meeting.get_location().__contains__('Meeting Held:'))






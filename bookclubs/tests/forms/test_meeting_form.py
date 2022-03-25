from datetime import date, timedelta

from django import forms
from django.test import TestCase

from bookclubs.forms import MeetingForm
from bookclubs.models import Meeting, User, Club, Book, MeetingAttendance


class MeetingFormTestCase(TestCase):
    """Testing the MeetingForm"""
    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_book.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.book = Book.objects.get(ISBN='0195153448')
        self.form_input = {
            'club': self.club,
            'book': self.book,
            'topic': 'alpha bravo charlie',
            'description': 'delta foxtrot golf hotel india',
            'meeting_status': 'OFF',
            'location': 'Bush House',
            'date': date.today() + timedelta(days=5),
            'time_start': '10:00',
            'duration': 11
        }

    def test_valid_new_meeting_form(self):
        form = MeetingForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_meeting_form_must_save_correctly(self):
        self.client.login(username=self.user.username, password="Password123")
        form = MeetingForm(data=self.form_input)
        before_count_meeting = Meeting.objects.count()
        before_count_attendance = MeetingAttendance.objects.count()
        form.original_save(self.user, self.club, self.book)
        after_count_meeting = Meeting.objects.count()
        after_count_attendance = MeetingAttendance.objects.count()
        self.assertEqual(after_count_meeting, before_count_meeting + 1)
        self.assertEqual(after_count_attendance, before_count_attendance + 1)
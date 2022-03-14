from django import forms
from django.test import TestCase

from bookclubs.forms import NewMeetingForm
from bookclubs.models import Meeting, User, Club, Book


class NewMeetingFormTestCase(TestCase):
    """Testing the NewMeetingForm"""
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
            'meeting_status': False,
            'location': 'Bush House',
            'date': '12/01/2023',
            'time_start': '10:00',
            'time_end': '11:00'
        }

    def test_valid_new_meeting_form(self):
        form = NewMeetingForm(data=self.form_input)
        self.assertTrue(form.is_valid())

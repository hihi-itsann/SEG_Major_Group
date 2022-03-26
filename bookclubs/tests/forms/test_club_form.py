from django.test import TestCase

from bookclubs.forms import ClubForm
from bookclubs.models import User, Club


class ClubFormTestCase(TestCase):
    """Testing the ClubForm"""

    def setUp(self):
        self.form_input = {
            'club_name': 'club1',
            'meeting_status': 'ONL',
            'location': 'location',
            'city': 'city1',
            'country': 'country1',
            'public_status': 'PUB',
            'genre': 'Non-Fiction',
            'description': 'description',
        }

    def test_form_contains_required_fields(self):
        form = ClubForm()
        self.assertIn('club_name', form.fields)
        self.assertIn('meeting_status', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('city', form.fields)
        self.assertIn('country', form.fields)
        self.assertIn('public_status', form.fields)
        self.assertIn('genre', form.fields)
        self.assertIn('description', form.fields)

    def test_form_accepts_form_input(self):
        form = ClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_club_name(self):
        self.form_input['club_name'] = ''
        form = ClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_bad_club_name(self):
        self.form_input['club_name'] = 'Bad'
        form = ClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())


from django import forms
from django.test import TestCase

from bookclubs.forms import ApplicationForm
from bookclubs.models import Application, User, Club


class ApplicationFormTestCase(TestCase):
    """Testing the ApplicationForm"""
    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.form_input = {
            'user': self.user,
            'club': self.club,
            'statement': 'Hello, I would like to join this club.'
        }

    def test_valid_application_form(self):
        form = ApplicationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_application_statement_is_charfield(self):
        form = ApplicationForm()
        name = form.fields['statement']
        self.assertTrue(isinstance(name, forms.CharField))

    def test_application_form_rejects_blank_statement(self):
        self.form_input['statement'] = ''
        form = ApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_application_form_must_save_correctly(self):
        self.client.login(username=self.user.email, password="Password123")
        form = ApplicationForm(data=self.form_input)
        before_count = Application.objects.count()
        form.original_save(self.user, self.club)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count + 1)
        application = Application.objects.get(user=self.user, club=self.club)
        self.assertEqual(application.statement, 'Hello, I would like to join this club.')
        self.assertEqual(application.status, 'P')

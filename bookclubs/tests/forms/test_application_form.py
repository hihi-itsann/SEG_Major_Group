from django import forms
from django.test import TestCase

from bookclubs.forms import NewApplicationForm, UpdateApplicationForm
from bookclubs.models import Application, User, Club


class NewApplicationFormTestCase(TestCase):
    """Testing the NewApplicationForm"""
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

    def test_valid_new_application_form(self):
        form = NewApplicationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_statement_is_charfield(self):
        form = NewApplicationForm()
        name = form.fields['statement']
        self.assertTrue(isinstance(name, forms.CharField))

    def test_form_rejects_blank_statement(self):
        self.form_input['statement'] = ''
        form = NewApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_application_form_must_save_correctly(self):
        self.client.login(username=self.user.email, password="Password123")
        form = NewApplicationForm(data=self.form_input)
        before_count = Application.objects.count()
        form.save(self.user, self.club)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count + 1)
        application = Application.objects.get(user=self.user, club=self.club)
        self.assertEqual(application.statement, 'Hello, I would like to join this club.')
        self.assertEqual(application.status, 'P')


class UpdateApplicationFormTestCase(TestCase):
    """Testing the UpdateApplicationForm"""
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
            'statement': 'Hello, I am editing my statement.'
        }

    def test_valid_update_application_form(self):
        form = UpdateApplicationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_statement_is_charfield(self):
        form = UpdateApplicationForm()
        name = form.fields['statement']
        self.assertTrue(isinstance(name, forms.CharField))

    def test_form_rejects_blank_statement(self):
        self.form_input['statement'] = ''
        form = UpdateApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_update_application_form_must_save_correctly(self):
        self.client.login(username=self.user.username, password="Password123")
        new_application_form = NewApplicationForm(
            {
                'user': self.user,
                'club': self.club,
                'statement': 'Hello, I would like to join this club.'
            }
        )
        new_application_form.save(self.user, self.club)
        update_application_form = UpdateApplicationForm(self.form_input)
        before_count = Application.objects.count()
        update_application_form.save(self.user, self.club)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)
        application = Application.objects.get(user=self.user, club=self.club)
        self.assertEqual(application.statement, 'Hello, I am editing my statement.')
        self.assertEqual(application.status, 'P')

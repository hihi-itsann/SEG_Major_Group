from datetime import date

from django import forms
from django.test import TestCase

from bookclubs.forms import UserForm
from bookclubs.models import User


class UserFormTestCase(TestCase):
    """Unit tests of the UserForm."""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe',
            'email': 'janedoe@example.org',
            'bio': 'My bio',
            'dob': '2002-07-14',
            'gender': 'F',
            'location': 'York',
            'meeting_preference': 'P',
        }

    def test_form_has_necessary_fields(self):
        form = UserForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)
        self.assertIn('dob', form.fields)
        dateBirth_field = form.fields['dob']
        self.assertTrue(isinstance(dateBirth_field, forms.DateField))
        self.assertIn('gender', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('meeting_preference', form.fields)

    def test_valid_user_form(self):
        form = UserForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'badusername'
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        user = User.objects.get(username='@johndoe')
        form = UserForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.username, '@janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertEqual(user.bio, 'My bio')
        self.assertEqual(user.dob, date(2002, 7, 14))
        self.assertEqual(user.gender, 'F')
        self.assertEqual(user.location, 'York')
        self.assertEqual(user.meeting_preference, 'P')

from django.test import TestCase
from bookclubs.models import User, Book, Rating
from bookclubs.forms import RateForm

class RateFormTestCase(TestCase):
    
    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.form_input = {
            'rate':9,
        }

    def test_form_contains_required_fields(self):
        form = RateForm()
        self.assertIn('rate', form.fields)

    def test_form_application_lists_valid_input(self):
        form = RateForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_rate_but_the_default_value_is_0(self):
        self.form_input['rate'] = ''
        form = RateForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.instance.rate, 0)

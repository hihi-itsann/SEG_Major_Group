from django.test import TestCase

from bookclubs.forms import RateReviewForm
from bookclubs.models import User, Book


class RateReviewFormTestCase(TestCase):
    """Unit tests for the RateReviewForm"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.form_input = {
            'rate': 9,
            'review': 'this is a book review.'
        }

    def test_form_contains_required_fields(self):
        form = RateReviewForm()
        self.assertIn('rate', form.fields)
        self.assertIn('review', form.fields)

    def test_form_lists_valid_input(self):
        form = RateReviewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_rate_but_the_default_value_is_0(self):
        self.form_input['rate'] = ''
        form = RateReviewForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.instance.rate, 0)

    def test_form_rejects_overlong_review(self):
        form_input = {'review': 'x' * 521}
        form = RateReviewForm(data=form_input)
        self.assertFalse(form.is_valid())

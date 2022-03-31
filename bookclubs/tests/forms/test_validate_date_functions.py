from datetime import date, timedelta

from django.forms import ValidationError
from django.test import TestCase

from bookclubs.forms import validate_date_not_in_past, validate_date_not_in_future


class ValidateDateFunctionsTestCase(TestCase):
    """Unit tests for the functions which validate whether a date"""

    def setUp(self):
        self.past_date = date.today() - timedelta(days=5)
        self.future_date = date.today() + timedelta(days=5)

    def test_not_in_future(self):
        with self.assertRaises(ValidationError) as context:
            validate_date_not_in_future(self.past_date)
        self.assertTrue('Date needs to be in the future.' in context.exception)

    def test_not_in_past(self):
        with self.assertRaises(ValidationError) as context:
            validate_date_not_in_past(self.future_date)
        self.assertTrue('Date needs to be in the past.' in context.exception)

from django.test import TestCase
from django.forms import ValidationError
from bookclubs.forms import validate_date_not_in_past, validate_date_not_in_future
from datetime import date, timedelta


class ValidateDateFunctionsTestCase(TestCase):

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

from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Club, Application


class ApplicationModelTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.application = Application.objects.create(
            user=self.user,
            club=self.club,
            statement='[Statement]',
            status='P'
        )



    def test_statement_can_be_blank(self):
        self.application.statement = ''
        self._assert_application_is_valid()

    def test_change_status(self):
        self.application.change_status('P')
        self.assertEqual(self.application.status, 'P')
        self.application.change_status('A')
        self.assertEqual(self.application.status, 'A')
        self.application.change_status('R')
        self.assertEqual(self.application.status, 'R')
        self.application.change_status('Z')
        self.assertEqual(self.application.status, 'P')

    def _assert_application_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.application.full_clean()

    def _assert_application_is_valid(self):
        try:
            self.application.full_clean()
        except ValidationError:
            self.fail('Test application should be valid')
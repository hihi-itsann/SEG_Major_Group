from django.core.exceptions import ValidationError
from django.test import TestCase
from libgravatar import Gravatar

from bookclubs.models import User


class UserModelTestCase(TestCase):
    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def test_valid_user(self):
        self._assert_user_is_valid()

    # test for username
    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_username_can_be_30_characters_long(self):
        self.user.username = '@' + 'x' * 29  # a string that contains 29 time character 'X'
        self._assert_user_is_valid()

    def test_username_cannot__be_over_30_characters_long(self):
        self.user.username = '@' + 'x' * 30
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.username = second_user.username
        self.user.username = '@janedoe'
        self._assert_user_is_invalid()

    def test_username_must_start_with_at_symbol(self):
        self.user.username = 'johndoe'
        self._assert_user_is_invalid()

    def test_username_must_contains_only_alphanumerical_after_at_(self):
        self.user.username = '@john!doe'
        self._assert_user_is_invalid()

    def test_username_must_contain_at_least_3_alphanumerical_after_at(self):
        self.user.username = '@jo'
        self._assert_user_is_invalid()

    def test_username_may_contain_numbers(self):
        self.user.username = '@johndoe2'
        self._assert_user_is_valid()

    def test_username_must_contain_only_1_at(self):
        self.user.username = '@@johndoe'
        self._assert_user_is_invalid()

    # test for first name
    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters_long(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    # test for last name
    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.last_name = second_user.first_name
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters_long(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()

    # test for email
    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.email = second_user.email
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    # test for bio
    def test_bio_may_be_blank(self):
        self.user.bio = ''
        self._assert_user_is_valid()

    def test_bio_need_not_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.bio = second_user.bio
        self._assert_user_is_valid()

    def test_bio_may_contain_520_characters(self):
        self.user.bio = 'x' * 520
        self._assert_user_is_valid()

    def test_bio_must_not_contain_more_than_520_characters_long(self):
        self.user.bio = 'x' * 521
        self._assert_user_is_invalid()

    # test for date of birth
    def test_dob_may_be_blank(self):
        self.user.dob = ''
        self._assert_user_is_valid()

    def test_dob_may_be_null(self):
        self.user.dob = None
        self._assert_user_is_valid()

    def test_dob_need_not_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.dob = second_user.dob
        self._assert_user_is_valid()

    # test for gender
    def test_gender_may_be_blank(self):
        self.user.gender = ''
        self._assert_user_is_valid()

    def test_gender_need_not_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.gender = second_user.gender
        self._assert_user_is_valid()

    def test_gender_may_contain_1_characters(self):
        self.user.gender = 'F' * 1
        self._assert_user_is_valid()

    def test_gender_must_not_contain_more_than_1_characters_long(self):
        self.user.gender = 'F' * 2
        self._assert_user_is_invalid()

    def test_gender_must_be_chose_from_list(self):
        self.user.gender = 'F'
        self._assert_user_is_valid()
        self.user.gender = 'M'
        self._assert_user_is_valid()
        self.user.gender = 'O'
        self._assert_user_is_valid()
        self.user.gender = 'A'
        self._assert_user_is_invalid()
        self.user.gender = 'B'
        self._assert_user_is_invalid()

    # test for location
    def test_location_may_be_blank(self):
        self.user.location = ''
        self._assert_user_is_valid()

    def test_location_need_not_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.location = second_user.location
        self._assert_user_is_valid()

    def test_location_may_contain_50_characters(self):
        self.user.location = 'x' * 50
        self._assert_user_is_valid()

    def test_location_must_not_contain_more_than_50_characters_long(self):
        self.user.location = 'x' * 51
        self._assert_user_is_invalid()

    # test for meeting preference
    def test_meeting_preference_may_be_blank(self):
        self.user.meeting_preference = ''
        self._assert_user_is_valid()

    def test_meeting_preference_need_not_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.meeting_preference = second_user.meeting_preference
        self._assert_user_is_valid()

    def test_meeting_preference_may_contain_1_characters(self):
        self.user.meeting_preference = 'O' * 1
        self._assert_user_is_valid()

    def test_meeting_preference_must_not_contain_more_than_1_characters_long(self):
        self.user.meeting_preference = 'O' * 2
        self._assert_user_is_invalid()

    def test_meeting_preference_must_be_chose_from_list(self):
        self.user.meeting_preference = 'O'
        self._assert_user_is_valid()
        self.user.meeting_preference = 'P'
        self._assert_user_is_valid()
        self.user.meeting_preference = 'A'
        self._assert_user_is_invalid()
        self.user.meeting_preference = 'B'
        self._assert_user_is_invalid()

    # test for full_name method
    def test_get_full_name(self):
        self.assertEqual("John Doe", self.user.full_name())

    # test for gravatar
    def test_gravatar(self):
        user_gravatar_url = Gravatar(self.user.email).get_image(size=120, default='mp')
        size = user_gravatar_url.__sizeof__()
        self.assertEqual(user_gravatar_url, self.user.gravatar())
        self.assertEqual(size, self.user.gravatar().__sizeof__())

    # test for mini_gravatar
    def test_mini_gravatar(self):
        size = self.user.gravatar(size=60).__sizeof__()
        self.assertEqual(size, self.user.mini_gravatar().__sizeof__())

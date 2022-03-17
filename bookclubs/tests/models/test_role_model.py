from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Club, Role


class RoleModelTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.role = Role.objects.create(
            user=self.user,
            club=self.club,
            club_role='OWN'
        )

    def test_role_get_club_role(self):
        self.assertEqual(self.role.get_club_role(), 'Owner')
        self.role.club_role = 'MEM'
        self.assertEqual(self.role.get_club_role(), 'Member')
        self.role.club_role = 'MOD'
        self.assertEqual(self.role.get_club_role(), 'Moderator')
        self.role.club_role = 'BAN'
        self.assertEqual(self.role.get_club_role(), 'Banned')
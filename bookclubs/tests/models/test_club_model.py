from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Club, Role, Application


class ClubModelTestCase(TestCase):
    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(username='@johndoe')
        self.moderator = User.objects.get(username='@janedoe')
        self.member = User.objects.get(username='@alexdoe')
        self.club = Club.objects.create(
            club_name='Club Name',
            meeting_status='OFF',
            location='Bush House',
            city='London',
            country='United Kingdom',
            public_status='PRI',
            genre='Fiction',
            description='This is a club.'
        )
        Role.objects.create(user=self.owner, club=self.club, club_role='OWN')
        Role.objects.create(user=self.moderator, club=self.club, club_role='MOD')
        self.membership = Role.objects.create(user=self.member, club=self.club, club_role='MEM')

    def test_get_club_name(self):
        self.assertEqual(self.club.get_club_name(), 'Club Name')

    def test_get_club_role(self):
        self.assertEqual(self.club.get_club_role(self.owner), 'OWN')
        self.assertEqual(self.club.get_club_role(self.moderator), 'MOD')
        self.assertEqual(self.club.get_club_role(self.member), 'MEM')

    def test_toggle_member_on_banned(self):
        self.membership.delete()
        banned = Role.objects.create(user=self.member, club=self.club, club_role='BAN')
        self.club.toggle_member(self.member)
        banned.refresh_from_db()
        self.assertEqual(banned.club_role, 'BAN')

    def test_toggle_member(self):
        moderating = Role.objects.get(club=self.club, user=self.moderator)
        self.club.toggle_member(self.moderator)
        moderating.refresh_from_db()
        self.assertEqual(moderating.club_role, 'MEM')

    def test_toggle_moderator_on_banned(self):
        self.membership.delete()
        banned = Role.objects.create(user=self.member, club=self.club, club_role='BAN')
        self.club.toggle_moderator(self.member)
        banned.refresh_from_db()
        self.assertEqual(banned.club_role, 'BAN')

    def test_toggle_moderator(self):
        self.club.toggle_moderator(self.member)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.club_role, 'MOD')

    def test_ban_member_on_higher_role(self):
        ownership = Role.objects.get(club=self.club, user=self.owner)
        self.club.ban_member(self.owner)
        ownership.refresh_from_db()
        self.assertEqual(ownership.club_role, 'OWN')

    def test_ban_member(self):
        self.club.ban_member(self.member)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.club_role, 'BAN')

    def test_unban_member_on_not_banned_member(self):
        self.club.unban_member(self.member)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.club_role, 'MEM')

    def test_unban_member(self):
        self.membership.delete()
        Application.objects.create(user=self.member, club=self.club, statement="Joined and was banned", status='A')
        Role.objects.create(user=self.member, club=self.club, club_role='BAN')
        self.club.unban_member(self.member)
        self.assertEqual(Role.objects.filter(club=self.club, user=self.member).count(), 1)

    def test_transfer_ownership_on_member(self):
        ownership = Role.objects.get(club=self.club, user=self.owner)
        self.club.transfer_ownership(self.owner, self.member)
        self.membership.refresh_from_db()
        ownership.refresh_from_db()
        self.assertEqual(self.membership.club_role, 'MEM')
        self.assertEqual(ownership.club_role, 'OWN')

    def test_transfer_ownership(self):
        ownership = Role.objects.get(club=self.club, user=self.owner)
        moderating = Role.objects.get(club=self.club, user=self.moderator)
        self.club.transfer_ownership(self.owner, self.moderator)
        ownership.refresh_from_db()
        moderating.refresh_from_db()
        self.assertEqual(moderating.club_role, 'OWN')
        self.assertEqual(ownership.club_role, 'MOD')

    def test_remove_user_from_club_on_owner(self):
        ownership = Role.objects.get(club=self.club, user=self.owner)
        self.club.remove_user_from_club(self.owner)
        ownership.refresh_from_db()
        self.assertEqual(ownership.club_role, 'OWN')

    def test_remove_user_from_club(self):
        Application.objects.create(user=self.member, club=self.club, statement='Accepted', status='A')
        self.club.remove_user_from_club(self.member)
        self.assertEqual(Role.objects.filter(club=self.club, user=self.member).count(), 0)
        self.assertEqual(Application.objects.filter(club=self.club, user=self.member).count(), 0)

    def test_get_moderators(self):
        self.assertIn(self.moderator, self.club.get_moderators())

    def test_get_management(self):
        self.assertIn(self.moderator, self.club.get_management())
        self.assertIn(self.owner, self.club.get_management())

    def test_get_banned_members(self):
        self.membership.delete()
        Role.objects.create(user=self.member, club=self.club, club_role='BAN')
        self.assertIn(self.member, self.club.get_banned_members())

    def test_get_owner(self):
        self.assertIn(self.owner, self.club.get_owner())

from django.test import TestCase
from django.urls import reverse

from bookclubs.models import Club, User, Role


class ClubDeleteViewTestCase(TestCase):
    """Tests for the deletion of a club"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.user2 = User.objects.get(username='@janedoe')
        self.club1 = Club.objects.get(club_name='private_online')
        self.club2 = Club.objects.get(club_name='public_online')
        self.club3 = Club.objects.get(club_name='private_in-person')
        self.club4 = Club.objects.get(club_name='public_in-person')
        self.url1 = reverse('delete_club', kwargs={'club_name': self.club1.club_name})
        self.url2 = reverse('delete_club', kwargs={'club_name': self.club2.club_name})
        self.url3 = reverse('delete_club', kwargs={'club_name': self.club3.club_name})
        self.url4 = reverse('delete_club', kwargs={'club_name': self.club4.club_name})
        self._create_test_roles()

    def test_delete_club_url(self):
        self.assertEqual(reverse('delete_club', kwargs={'club_name': self.club1.club_name}),
                         f'/club/{self.club1.club_name}/delete/')
        self.assertEqual(reverse('delete_club', kwargs={'club_name': self.club2.club_name}),
                         f'/club/{self.club2.club_name}/delete/')
        self.assertEqual(reverse('delete_club', kwargs={'club_name': self.club3.club_name}),
                         f'/club/{self.club3.club_name}/delete/')
        self.assertEqual(reverse('delete_club', kwargs={'club_name': self.club4.club_name}),
                         f'/club/{self.club4.club_name}/delete/')

    def test_owner_delete_club1_feed(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.get(self.url1)
        after_count = Club.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(after_count, before_count - 1)

    def test_owner_delete_club2_feed(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.get(self.url2)
        after_count = Club.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(after_count, before_count - 1)

    def test_owner_delete_club3_feed(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.get(self.url3)
        after_count = Club.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(after_count, before_count - 1)

    def test_owner_delete_club4_feed(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.get(self.url4)
        after_count = Club.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(after_count, before_count - 1)

    def test_Moderator_cannot_delete_club1_feed(self):
        self.client.login(username=self.user2.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.get(self.url1)
        after_count = Club.objects.count()
        response_url = reverse('club_feed', kwargs={'club_name': self.club1.club_name})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertEqual(after_count, before_count)

    def test_Member_cannot_delete_club2_feed(self):
        self.client.login(username=self.user2.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.get(self.url2)
        after_count = Club.objects.count()
        response_url = reverse('club_feed', kwargs={'club_name': self.club2.club_name})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertEqual(after_count, before_count)

    def test_banner_cannot_delete_club3_feed(self):
        self.client.login(username=self.user2.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.get(self.url3)
        after_count = Club.objects.count()
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertEqual(after_count, before_count)

    def test_others_cannot_delete_club4_feed(self):
        self.client.login(username=self.user2.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.get(self.url4)
        after_count = Club.objects.count()
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertEqual(after_count, before_count)

    def test_Moderator_relationship_delete_when_club_delete(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Role.objects.count()
        response = self.client.get(self.url1)
        after_count = Role.objects.count()
        self.assertEqual(after_count, before_count - 2)

    def test_Member_relationship_delete_when_club_delete(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Role.objects.count()
        response = self.client.get(self.url2)
        after_count = Role.objects.count()
        self.assertEqual(after_count, before_count - 2)

    def test_banner_relationship_delete_when_club_delete(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Role.objects.count()
        response = self.client.get(self.url3)
        after_count = Role.objects.count()
        self.assertEqual(after_count, before_count - 2)

    def test_cannot_delete_no_exist_club(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        self.url5 = reverse('delete_club', kwargs={'club_name': 'club5'})
        response = self.client.get(self.url5)
        response_url = reverse('feed')
        after_count = Club.objects.count()
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertEqual(after_count, before_count)

    def _create_test_roles(self):
        Role.objects.create(
            club=self.club1,
            user=self.user,
            club_role='OWN',
        )

        Role.objects.create(
            club=self.club1,
            user=self.user2,
            club_role='MOD',
        )

        Role.objects.create(
            club=self.club2,
            user=self.user,
            club_role='OWN',
        )

        Role.objects.create(
            club=self.club2,
            user=self.user2,
            club_role='MEM',
        )

        Role.objects.create(
            club=self.club3,
            user=self.user,
            club_role='OWN',
        )

        Role.objects.create(
            club=self.club3,
            user=self.user2,
            club_role='BAN',
        )

        Role.objects.create(
            club=self.club4,
            user=self.user,
            club_role='OWN',
        )

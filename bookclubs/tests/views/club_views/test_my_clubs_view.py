from django.test import TestCase
from django.urls import reverse

from bookclubs.models import Club, User, Role
from bookclubs.tests.helpers import reverse_with_next


class MyClubViewTestCase(TestCase):
    """Tests for showing the clubs that the user is part of"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club1 = Club.objects.get(club_name='private_online')
        self.club2 = Club.objects.get(club_name='public_online')
        self.club3 = Club.objects.get(club_name='private_in-person')
        self.club4 = Club.objects.get(club_name='public_in-person')
        self.club5 = Club.objects.get(club_name='club5')
        self._create_test_roles()
        self.url = reverse('my_clubs')

    def test_my_clubs_url(self):
        self.assertEqual(reverse('my_clubs'), '/my_clubs/')

    def test_my_clubs(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs.html')
        clubs = response.context['clubs']
        self.assertEqual(len(response.context['clubs']), 3)

    def test_club_where_owner_shows_in_my_clubs(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs.html')
        clubs = response.context['clubs']
        self.assertEqual(len(response.context['clubs']), 3)
        role = Role.objects.get(user=self.user, club=self.club1)
        self.assertIn(role, clubs)

    def test_club_where_moderator_shows_in_my_clubs(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs.html')
        clubs = response.context['clubs']
        self.assertEqual(len(response.context['clubs']), 3)
        role = Role.objects.get(user=self.user, club=self.club3)
        self.assertIn(role, clubs)

    def test_club_where_member_shows_in_my_clubs(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs.html')
        clubs = response.context['clubs']
        self.assertEqual(len(response.context['clubs']), 3)
        role = Role.objects.get(user=self.user, club=self.club2)
        self.assertIn(role, clubs)

    def test_club_where_banned_from_club_does_not_show_in_my_clubs(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs.html')
        clubs = response.context['clubs']
        self.assertEqual(len(response.context['clubs']), 3)
        role = Role.objects.get(user=self.user, club=self.club4)
        self.assertNotIn(role, clubs)
        # self.assertFalse(self.assertIn(role, clubs))

    def test_club_where_there_is_no_relation_does_not_show_in_my_clubs(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs.html')
        clubs = response.context['clubs']
        self.assertEqual(len(response.context['clubs']), 3)
        num_clubs = clubs.count()
        club_list = []
        for club in clubs:
            club_list.append(club.club)
        self.assertNotIn(self.club5, club_list)

    def test_no_logging_cannot_get_my_clubs_url(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        # self.assertTemplateUsed(response, 'my_clubs.html')
        # clubs = response.context['clubs']
        # self.assertEqual(len(response.context['clubs']), 3)
        # num_clubs= clubs.count()
        # club_list=[]
        # for club in clubs:
        #     club_list.append(club.club)
        # self.assertNotIn(self.club5, club_list)

    def _create_test_roles(self):
        Role.objects.create(
            club=self.club1,
            user=self.user,
            club_role='OWN',
        )

        Role.objects.create(
            club=self.club2,
            user=self.user,
            club_role='MEM',
        )

        Role.objects.create(
            club=self.club3,
            user=self.user,
            club_role='MOD',
        )

        Role.objects.create(
            club=self.club4,
            user=self.user,
            club_role='BAN',
        )

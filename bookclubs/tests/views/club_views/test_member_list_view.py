from django.test import TestCase
from django.contrib.auth.hashers import check_password
from bookclubs.forms import ClubForm
from django.urls import reverse
from bookclubs.models import Club, User, Role
from bookclubs.tests.helpers import reverse_with_next


class MemberListViewTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.user2 = User.objects.get(username='@janedoe')
        self.user3 = User.objects.get(username='@Alexdoe')
        self.club1 =  Club.objects.get(club_name='private_online')
        self.club2 =  Club.objects.get(club_name='public_online')
        self.club3 =  Club.objects.get(club_name='private_in-person')
        self._create_test_rols()
        self.url = reverse('member_list',kwargs={'club_name':self.club1.club_name})


    def test_ban_from_club_url(self):
        self.assertEqual(self.url, f'/club/{self.club1.club_name}/member_list/')

    def test_get_member_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successfully_get_member_list_by_owner(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')
        self.assertEqual(len(response.context['roles']), 3)
        self.assertEqual(response.context['club'], self.club1)
        self.assertEqual(response.context['current_user'], self.user)
        self.assertEqual(response.context['current_user_role'], 'OWN')
        self.assertEqual(response.context['club_owner'], self.user)
        self.assertEqual(len(response.context['club_moderators']), 1)
        self.assertEqual(len(response.context['club_members']), 1)
        self.assertEqual(len(response.context['club_banned']), 0)
        self.assertTrue(response.context['is_owner'])
        self.assertTrue(response.context['roles_num']==3)


    def test_successfully_get_member_list_by_moderator(self):
        self.client.login(username=self.user2.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')
        self.assertEqual(len(response.context['roles']), 3)
        self.assertEqual(response.context['club'], self.club1)
        self.assertEqual(response.context['current_user'], self.user2)
        self.assertEqual(response.context['current_user_role'], 'MOD')
        self.assertEqual(response.context['club_owner'], self.user)
        self.assertEqual(len(response.context['club_moderators']), 1)
        self.assertEqual(len(response.context['club_members']), 1)
        self.assertEqual(len(response.context['club_banned']), 0)
        self.assertFalse(response.context['is_owner'])
        self.assertTrue(response.context['roles_num']==3)


    def test_successfully_get_member_list_by_member(self):
        self.client.login(username=self.user3.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')
        self.assertEqual(len(response.context['roles']), 3)
        self.assertEqual(response.context['club'], self.club1)
        self.assertEqual(response.context['current_user'], self.user3)
        self.assertEqual(response.context['current_user_role'], 'MEM')
        self.assertEqual(response.context['club_owner'], self.user)
        self.assertEqual(len(response.context['club_moderators']), 1)
        self.assertEqual(len(response.context['club_members']), 1)
        self.assertEqual(len(response.context['club_banned']), 0)
        self.assertFalse(response.context['is_owner'])
        self.assertTrue(response.context['roles_num']==3)


    def test_unsuccessfully_get_member_list_by_banner(self):
        self.client.login(username=self.user3.username, password='Password123')
        response_url = reverse('feed')
        self.url = reverse('member_list',kwargs={'club_name':self.club2.club_name})
        response = self.client.get(self.url)
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )


    def test_unsuccessfully_get_member_list_by_user_not_in_the_club(self):
        self.client.login(username=self.user2.username, password='Password123')
        response_url = reverse('feed')
        self.url = reverse('member_list',kwargs={'club_name':self.club3.club_name})
        response = self.client.get(self.url)
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        

    def test_unsuccessfully_get_member_list_of_non_exist_club(self):
        self.client.login(username=self.user2.username, password='Password123')
        response_url = reverse('feed')
        self.url = reverse('member_list',kwargs={'club_name':'club_non_exist'})
        response = self.client.get(self.url)
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )



    def _create_test_rols(self):
        Role.objects.create(
            club = self.club1,
            user = self.user,
            club_role = 'OWN',
            )


        Role.objects.create(
            club = self.club1,
            user = self.user2,
            club_role = 'MOD',
            )


        Role.objects.create(
            club = self.club1,
            user = self.user3,
            club_role = 'MEM',
            )

        Role.objects.create(
            club = self.club2,
            user = self.user,
            club_role = 'OWN',
            )

        Role.objects.create(
            club = self.club2,
            user = self.user2,
            club_role = 'MEM',
            )

        Role.objects.create(
            club = self.club2,
            user = self.user3,
            club_role = 'BAN',
            )

        Role.objects.create(
            club = self.club3,
            user = self.user,
            club_role = 'OWN',
            )

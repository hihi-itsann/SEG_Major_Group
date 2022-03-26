from django.test import TestCase
from django.contrib.auth.hashers import check_password
from bookclubs.forms import ClubForm
from django.urls import reverse
from bookclubs.models import Club, User, Role
from bookclubs.tests.helpers import reverse_with_next


class PromoteMemberViewTestCase(TestCase):

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
        self.club4 =  Club.objects.get(club_name='public_in-person')
        self._create_test_rols()
        self.url1 = reverse('promote_member',kwargs={'club_name':self.club2.club_name, 'user_id': self.user2.id})


    def test_promote_member_url(self):
        self.assertEqual(self.url1, f'/club/{self.club2.club_name}/promote/{self.user2.id}/')

    def test_get_transfer_ownership_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url1)
        response = self.client.get(self.url1)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successfully_promte_member_to_mod_by_owner(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url1, follow=True)
        response_url = reverse('member_list', kwargs={'club_name': self.club2.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertEqual(self.club2.get_club_role(self.user2), 'MOD')


    def test_unsuccessfully_promte_owner_to_mod_by_owner(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url2=reverse('promote_member',kwargs={'club_name':self.club1.club_name, 'user_id': self.user.id})
        response = self.client.post(self.url2, follow=True)
        response_url = reverse('member_list', kwargs={'club_name': self.club1.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertEqual(self.club1.get_club_role(self.user), 'OWN')
        roles = Role.objects.filter(club=self.club3)
        member_list = []
        for i in roles:
            member_list.append(i.user)
        self.assertIn(self.user, member_list)
        self.assertEqual(len(member_list),3)



    def test_no_change_promte_moderator_to_mod_by_owner(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url3=reverse('promote_member',kwargs={'club_name':self.club1.club_name, 'user_id': self.user2.id})
        response = self.client.post(self.url3, follow=True)
        response_url = reverse('member_list', kwargs={'club_name': self.club1.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertEqual(self.club1.get_club_role(self.user2), 'MOD')
        roles = Role.objects.filter(club=self.club3)
        member_list = []
        for i in roles:
            member_list.append(i.user)
        self.assertIn(self.user2, member_list)
        self.assertEqual(len(member_list),3)



    def test_unsuccessfully_promte_banner_to_mod_by_owner(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url3=reverse('promote_member',kwargs={'club_name':self.club3.club_name, 'user_id': self.user2.id})
        response = self.client.post(self.url3, follow=True)
        response_url = reverse('member_list', kwargs={'club_name': self.club3.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertEqual(self.club3.get_club_role(self.user2), 'BAN')
        roles = Role.objects.filter(club=self.club3)
        member_list = []
        for i in roles:
            member_list.append(i.user)
        self.assertIn(self.user2, member_list)
        self.assertEqual(len(member_list),3)



    def test_unsuccessfully_promte_non_exist_member_to_mod_by_owner(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url4=reverse('promote_member',kwargs={'club_name':self.club4.club_name, 'user_id': self.user2.id})
        response = self.client.post(self.url4, follow=True)
        response_url = reverse('member_list', kwargs={'club_name': self.club4.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        roles = Role.objects.filter(club=self.club4)
        member_list = []
        for i in roles:
            member_list.append(i.user)
        self.assertNotIn(self.user2, member_list)
        self.assertEqual(len(member_list),2)


    def test_unsuccessfully_promte_member_to_mod_by_moderator(self):
        self.client.login(username=self.user2.username, password='Password123')
        self.url5=reverse('promote_member',kwargs={'club_name':self.club1.club_name, 'user_id': self.user3.id})
        response = self.client.post(self.url5, follow=True)
        response_url = reverse('club_feed', kwargs={'club_name': self.club1.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        roles = Role.objects.filter(club=self.club1)
        member_list = []
        for i in roles:
            member_list.append(i.user)
        self.assertIn(self.user3, member_list)
        self.assertEqual(len(member_list),3)
        self.assertEqual(self.club1.get_club_role(self.user3), 'MEM')


    def test_unsuccessfully_promte_member_to_mod_by_member(self):
        self.client.login(username=self.user2.username, password='Password123')
        self.url6=reverse('promote_member',kwargs={'club_name':self.club2.club_name, 'user_id': self.user3.id})
        response = self.client.post(self.url6, follow=True)
        response_url = reverse('club_feed', kwargs={'club_name': self.club2.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        roles = Role.objects.filter(club=self.club2)
        member_list = []
        for i in roles:
            member_list.append(i.user)
        self.assertIn(self.user3, member_list)
        self.assertEqual(len(member_list),3)
        self.assertEqual(self.club2.get_club_role(self.user3), 'MEM')


    def test_unsuccessfully_promte_member_to_mod_by_banner(self):
        self.client.login(username=self.user2.username, password='Password123')
        self.url7=reverse('promote_member',kwargs={'club_name':self.club3.club_name, 'user_id': self.user3.id})
        response = self.client.post(self.url7, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        roles = Role.objects.filter(club=self.club3)
        member_list = []
        for i in roles:
            member_list.append(i.user)
        self.assertIn(self.user3, member_list)
        self.assertEqual(len(member_list),3)
        self.assertEqual(self.club3.get_club_role(self.user3), 'MEM')


    def test_unsuccessfully_promte_member_to_mod_by_not_exist_member(self):
        self.client.login(username=self.user2.username, password='Password123')
        self.url8=reverse('promote_member',kwargs={'club_name':self.club4.club_name, 'user_id': self.user3.id})
        response = self.client.post(self.url8, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        roles = Role.objects.filter(club=self.club4)
        member_list = []
        for i in roles:
            member_list.append(i.user)
        self.assertIn(self.user3, member_list)
        self.assertEqual(len(member_list),2)
        self.assertEqual(self.club4.get_club_role(self.user3), 'MEM')


    def test_unsuccessfully_promte_member_in_non_exist_club(self):
        self.client.login(username=self.user2.username, password='Password123')
        self.url8=reverse('promote_member',kwargs={'club_name':'club5', 'user_id': '10'})
        response = self.client.post(self.url8, follow=True)
        response_url = reverse('feed')
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
            club = self.club2,
            user = self.user,
            club_role = 'OWN',
            )


        Role.objects.create(
            club = self.club3,
            user = self.user,
            club_role = 'OWN',
            )


        Role.objects.create(
            club = self.club4,
            user = self.user,
            club_role = 'OWN',
            )

        Role.objects.create(
            club = self.club1,
            user = self.user2,
            club_role = 'MOD',
            )

        Role.objects.create(
            club = self.club2,
            user = self.user2,
            club_role = 'MEM',
            )

        Role.objects.create(
            club = self.club3,
            user = self.user2,
            club_role = 'BAN',
            )

        Role.objects.create(
            club = self.club1,
            user = self.user3,
            club_role = 'MEM',
            )

        Role.objects.create(
            club = self.club2,
            user = self.user3,
            club_role = 'MEM',
            )

        Role.objects.create(
            club = self.club3,
            user = self.user3,
            club_role = 'MEM',
            )

        Role.objects.create(
            club = self.club4,
            user = self.user3,
            club_role = 'MEM',
            )

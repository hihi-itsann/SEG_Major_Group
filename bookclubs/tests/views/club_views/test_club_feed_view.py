from django.test import TestCase
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from bookclubs.models import Club, User, Role
from bookclubs.tests.helpers import reverse_with_next

class ClubFeedViewTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username=self.user.username, password='Password123')
        self.user2 = User.objects.get(username='@janedoe')
        self.user3 = User.objects.get(username='@Alexdoe')
        self.club1 =  Club.objects.get(club_name='private_online')
        self.club2 =  Club.objects.get(club_name='public_online')
        self.club3 =  Club.objects.get(club_name='private_in-person')
        self.club4 =  Club.objects.get(club_name='public_in-person')
        # user3=self._create_third_user()
        # print(user3.userID)
        self._create_test_rols()
        self.url1 = reverse('club_feed',kwargs={'club_name':self.club1.club_name})
        self.url2 = reverse('club_feed',kwargs={'club_name':self.club2.club_name})
        self.url3 = reverse('club_feed',kwargs={'club_name':self.club3.club_name})
        self.url4 = reverse('club_feed',kwargs={'club_name':self.club4.club_name})

    def test_create_club_url(self):
        self.assertEqual(reverse('club_feed',kwargs={'club_name':self.club1.club_name}), f'/club/{self.club1.club_name}/feed/')
        self.assertEqual(reverse('club_feed',kwargs={'club_name':self.club2.club_name}), f'/club/{self.club2.club_name}/feed/')
        self.assertEqual(reverse('club_feed',kwargs={'club_name':self.club3.club_name}), f'/club/{self.club3.club_name}/feed/')
        self.assertEqual(reverse('club_feed',kwargs={'club_name':self.club4.club_name}), f'/club/{self.club4.club_name}/feed/')

    def test_get_club1_feed(self):
        response = self.client.get(self.url1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_feed.html')
        self.assertEqual(response.context['club'],self.club1)
        self.assertTrue(response.context['is_moderator']==False)
        self.assertEqual(response.context['is_owner'],True)
        self.assertEqual(len(response.context['members']), 0)
        self.assertEqual(len(response.context['management']), 1)

    def test_get_club2_feed(self):
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_feed.html')
        self.assertEqual(response.context['club'],self.club2)
        self.assertTrue(response.context['is_moderator']==False)
        self.assertEqual(response.context['is_owner'],False)
        self.assertEqual(len(response.context['members']), 1)
        self.assertEqual(len(response.context['management']), 0)

    def test_get_club3_feed(self):
        response = self.client.get(self.url3)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_feed.html')
        self.assertEqual(response.context['club'],self.club3)
        self.assertTrue(response.context['is_moderator']==True)
        self.assertEqual(response.context['is_owner'],False)
        self.assertEqual(len(response.context['members']), 0)
        self.assertEqual(len(response.context['management']), 1)

    def test_get_club4_feed(self):
        response = self.client.get(self.url4)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_feed.html')
        self.assertEqual(response.context['club'],self.club4)
        self.assertTrue(response.context['is_moderator']==False)
        self.assertEqual(response.context['is_owner'],True)
        self.assertEqual(len(response.context['members']), 0)
        self.assertEqual(len(response.context['management']), 1)

    def test_other_user_cannot_get_club1_feed(self):
        self.client.login(username=self.user2.username, password='Password123')
        response = self.client.get(self.url1)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_other_user_cannot_get_club2_feed(self):
        self.client.login(username=self.user2.username, password='Password123')
        response = self.client.get(self.url2)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_other_user_cannot_get_club3_feed(self):
        self.client.login(username=self.user2.username, password='Password123')
        response = self.client.get(self.url3)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_other_user_cannot_get_club4_feed(self):
        self.client.login(username=self.user2.username, password='Password123')
        response = self.client.get(self.url4)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_banned_user_cannot_get_club1_feed(self):
        self.client.login(username=self.user3.username, password='Password123')
        response = self.client.get(self.url1)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_banned_user_cannot_get_club2_feed(self):
        self.client.login(username=self.user3.username, password='Password123')
        response = self.client.get(self.url2)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_banned_user_cannot_get_club3_feed(self):
        self.client.login(username=self.user3.username, password='Password123')
        response = self.client.get(self.url3)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_banned_user_cannot_get_club4_feed(self):
        self.client.login(username=self.user3.username, password='Password123')
        response = self.client.get(self.url4)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
    # def _create_third_user(self):
    #     User.objects.create(
    #         userID = 3,
    #         username = "@testuser3",
    #         first_name = "test",
    #         last_name = "user",
    #         email = "testuser3@example.org",
    #         bio = "Hello, I'm testuser3.",
    #         dob = "2002-07-14",
    #         gender = "M",
    #         location = "Bush house",
    #         city = "London",
    #         country = "UK",
    #         meeting_preference= "P",
    #         password= "Password123",
    #         is_active= true
    #         )
    def test_cannot_get_no_eixts_club_feed(self):
        self.client.login(username=self.user3.username, password='Password123')
        self.url5=reverse('club_feed',kwargs={'club_name':'club5'})
        response = self.client.get(self.url5)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)


    def _create_test_rols(self):
        Role.objects.create(
            club = self.club1,
            user = self.user,
            club_role = 'OWN',
            )

        Role.objects.create(
            club = self.club1,
            user = self.user3,
            club_role = 'BAN',
            )

        Role.objects.create(
            club = self.club2,
            user = self.user,
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
            club_role = 'MOD',
            )

        Role.objects.create(
            club = self.club3,
            user = self.user3,
            club_role = 'BAN',
            )

        Role.objects.create(
            club = self.club4,
            user = self.user,
            club_role = 'OWN',
            )

        Role.objects.create(
            club = self.club4,
            user = self.user3,
            club_role = 'BAN',
            )

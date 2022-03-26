from django.test import TestCase
from django.contrib.auth.hashers import check_password
from bookclubs.forms import ClubForm
from django.urls import reverse
from bookclubs.models import Club, User, Book, Role
from bookclubs.tests.helpers import reverse_with_next

class UpdateClubViewTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.user2 = User.objects.get(username='@janedoe')
        self.club1 =  Club.objects.get(club_name='private_online')
        self.club2 =  Club.objects.get(club_name='public_online')
        self.club3 =  Club.objects.get(club_name='private_in-person')
        self.club4 =  Club.objects.get(club_name='public_in-person')
        self._create_test_rols()
        self.url1 = reverse('update_club_info',kwargs={'club_name':self.club1.club_name})
        self.url2 = reverse('update_club_info',kwargs={'club_name':self.club2.club_name})
        self.url3 = reverse('update_club_info',kwargs={'club_name':self.club3.club_name})
        self.url4 = reverse('update_club_info',kwargs={'club_name':self.club4.club_name})

        self.form_input_online_public = {
            'club_name': 'club1',
            'meeting_status': 'ONL',
            'location': 'location',
            'city': 'city1',
            'country': 'country1',
            'public_status': 'PUB',
            'genre': 'Non-Fiction',
            # 'genre': 'Social Science',

            'description': 'description',
        }

        self.form_input_online_private = {
            'club_name': 'club1',
            'meeting_status': 'ONL',
            'location': 'location',
            'city': 'city1',
            'country': 'country1',
            'public_status': 'PRI',
            'genre': 'Fiction',
            'description': 'description',
        }

        self.form_input_in_person_private = {
            'club_name': 'club1',
            'meeting_status': 'OFF',
            'location': 'location',
            'city': 'city1',
            'country': 'country1',
            'public_status': 'PRI',
            'genre': 'Fiction',
            'description': 'description',
        }

        self.form_input_in_person_public = {
            'club_name': 'club1',
            'meeting_status': 'OFF',
            'location': 'location',
            'city': 'city1',
            'country': 'country1',
            'public_status': 'PUB',
            # 'genre': 'Social Science',
            'genre': 'Non-Fiction',
            'description': 'description',
        }

    def test_update_create_club_url(self):
        self.assertEqual(reverse('update_club_info',kwargs={'club_name':self.club1.club_name}), f'/club/{self.club1.club_name}/update_club_info/')
        self.assertEqual(reverse('update_club_info',kwargs={'club_name':self.club2.club_name}), f'/club/{self.club2.club_name}/update_club_info/')
        self.assertEqual(reverse('update_club_info',kwargs={'club_name':self.club3.club_name}), f'/club/{self.club3.club_name}/update_club_info/')
        self.assertEqual(reverse('update_club_info',kwargs={'club_name':self.club4.club_name}), f'/club/{self.club4.club_name}/update_club_info/')

    def test_get_update_create_club1_url(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_club_info.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertEqual(form.instance, self.club1)

    def test_get_update_create_club2_url(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_club_info.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertEqual(form.instance, self.club2)

    def test_get_update_create_club3_url(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url3)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_club_info.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertEqual(form.instance, self.club3)

    def test_get_update_create_club4_url(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url4)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_club_info.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertEqual(form.instance, self.club4)

    def test_unsuccesful_club1_wrong_name_update(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input_online_public['club_name'] = 'BAD'
        before_count = Club.objects.count()
        response = self.client.post(self.url1, self.form_input_online_public)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_club_info.html')
        form = response.context['form']
        club_name = response.context['club_name']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertTrue(club_name, self.club1.club_name)
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.club1.club_name, 'private_online')
        self.assertEqual(self.club1.meeting_status, 'ONL')
        self.assertEqual(self.club1.location, 'Bush House')
        self.assertEqual(self.club1.public_status, 'PRI')
        self.assertEqual(self.club1.genre, 'Fiction')
        self.assertEqual(self.club1.description, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ipsum dolor sit amet consectetur adipiscing. Mauris in aliquam sem fringilla ut morbi tincidunt augue interdum.')

    def test_unsuccesful_club2_wrong_meeting_status_update(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input_online_private['meeting_status'] = 'BAD'
        before_count = Club.objects.count()
        response = self.client.post(self.url2, self.form_input_online_private)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_club_info.html')
        form = response.context['form']
        club_name = response.context['club_name']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertTrue(club_name, self.club2.club_name)
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.club2.club_name, 'public_online')
        self.assertEqual(self.club2.meeting_status, 'ONL')
        self.assertEqual(self.club2.location, 'Bush House')
        self.assertEqual(self.club2.public_status, 'PUB')
        self.assertEqual(self.club2.genre, 'Fiction')
        self.assertEqual(self.club2.description, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ipsum dolor sit amet consectetur adipiscing. Mauris in aliquam sem fringilla ut morbi tincidunt augue interdum.')

    def test_unsuccesful_club3_wrong_location_update(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input_online_private['location'] = ''
        before_count = Club.objects.count()
        response = self.client.post(self.url2, self.form_input_online_private)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_club_info.html')
        form = response.context['form']
        club_name = response.context['club_name']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertTrue(club_name, self.club3.club_name)
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.club3.club_name, 'private_in-person')
        self.assertEqual(self.club3.meeting_status, 'OFF')
        self.assertEqual(self.club3.location, 'Bush House')
        self.assertEqual(self.club3.public_status, 'PRI')
        self.assertEqual(self.club3.genre, 'Fiction')
        self.assertEqual(self.club3.description, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ipsum dolor sit amet consectetur adipiscing. Mauris in aliquam sem fringilla ut morbi tincidunt augue interdum.')

    def test_unsuccesful_club4_wrong_genre_update(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input_online_private['genre'] = ''
        before_count = Club.objects.count()
        response = self.client.post(self.url2, self.form_input_online_private)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_club_info.html')
        form = response.context['form']
        club_name = response.context['club_name']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertTrue(club_name, self.club4.club_name)
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.club4.club_name, 'public_in-person')
        self.assertEqual(self.club4.meeting_status, 'OFF')
        self.assertEqual(self.club4.location, 'Bush House')
        self.assertEqual(self.club4.public_status, 'PUB')
        self.assertEqual(self.club4.genre, 'Fiction')
        self.assertEqual(self.club4.description, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ipsum dolor sit amet consectetur adipiscing. Mauris in aliquam sem fringilla ut morbi tincidunt augue interdum.')

    def test_moderator_cannot_update_club1(self):
        self.client.login(username=self.user2.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url1, self.form_input_online_public)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_feed', kwargs={'club_name': self.club1.club_name})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.user.refresh_from_db()
        self.assertEqual(self.club1.club_name, 'private_online')
        self.assertEqual(self.club1.meeting_status, 'ONL')
        self.assertEqual(self.club1.location, 'Bush House')
        self.assertEqual(self.club1.public_status, 'PRI')
        self.assertEqual(self.club1.genre, 'Fiction')
        self.assertEqual(self.club1.description, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ipsum dolor sit amet consectetur adipiscing. Mauris in aliquam sem fringilla ut morbi tincidunt augue interdum.')

    def test_member_cannot_update_club2(self):
        self.client.login(username=self.user2.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url2, self.form_input_online_public)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_feed', kwargs={'club_name': self.club2.club_name})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.user.refresh_from_db()
        self.assertEqual(self.club2.club_name, 'public_online')
        self.assertEqual(self.club2.meeting_status, 'ONL')
        self.assertEqual(self.club2.location, 'Bush House')
        self.assertEqual(self.club2.public_status, 'PUB')
        self.assertEqual(self.club2.genre, 'Fiction')
        self.assertEqual(self.club2.description, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ipsum dolor sit amet consectetur adipiscing. Mauris in aliquam sem fringilla ut morbi tincidunt augue interdum.')

    def test_banner_cannot_update_club3(self):
        self.client.login(username=self.user2.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url3, self.form_input_online_public)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.user.refresh_from_db()
        self.assertEqual(self.club3.club_name, 'private_in-person')
        self.assertEqual(self.club3.meeting_status, 'OFF')
        self.assertEqual(self.club3.location, 'Bush House')
        self.assertEqual(self.club3.public_status, 'PRI')
        self.assertEqual(self.club3.genre, 'Fiction')
        self.assertEqual(self.club3.description, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ipsum dolor sit amet consectetur adipiscing. Mauris in aliquam sem fringilla ut morbi tincidunt augue interdum.')

    def test_non_membership_cannot_update_club4(self):
        self.client.login(username=self.user2.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url4, self.form_input_online_public)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.user.refresh_from_db()
        self.assertEqual(self.club4.club_name, 'public_in-person')
        self.assertEqual(self.club4.meeting_status, 'OFF')
        self.assertEqual(self.club4.location, 'Bush House')
        self.assertEqual(self.club4.public_status, 'PUB')
        self.assertEqual(self.club4.genre, 'Fiction')
        self.assertEqual(self.club4.description, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ipsum dolor sit amet consectetur adipiscing. Mauris in aliquam sem fringilla ut morbi tincidunt augue interdum.')

    def test_cannot_update_non_exist_club(self):
        self.client.login(username=self.user2.username, password='Password123')
        self.url5 = reverse('update_club_info',kwargs={'club_name':'non_exist'})
        before_count = Club.objects.count()
        response = self.client.post(self.url5, self.form_input_online_public)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.user.refresh_from_db()

    def test_succesful_club1_update(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url1, self.form_input_online_public, follow=True)
        after_count = Club.objects.count()
        self.user.refresh_from_db()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_feed', kwargs={'club_name': 'club1'})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        # response = self.client.post(self.url, self.form_input_online_public)
        self.assertTemplateUsed(response, 'club_feed.html')
        self.club1 = Club.objects.get(club_name='club1')
        self.assertEqual(self.club1.meeting_status, 'ONL')
        self.assertEqual(self.club1.city, 'city1')
        self.assertEqual(self.club1.country, 'country1')
        self.assertEqual(self.club1.location, 'location')
        self.assertEqual(self.club1.public_status, 'PUB')
        self.assertEqual(self.club1.genre, 'Non-Fiction')
        self.assertEqual(self.club1.description, 'description')

    def test_succesful_club2_update(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url2, self.form_input_online_private, follow=True)
        after_count = Club.objects.count()
        self.user.refresh_from_db()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_feed', kwargs={'club_name': 'club1'})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        # response = self.client.post(self.url, self.form_input_online_public)
        self.assertTemplateUsed(response, 'club_feed.html')
        self.club2 = Club.objects.get(club_name='club1')
        self.assertEqual(self.club2.meeting_status, 'ONL')
        self.assertEqual(self.club2.city, 'city1')
        self.assertEqual(self.club2.country, 'country1')
        self.assertEqual(self.club2.location, 'location')
        self.assertEqual(self.club2.public_status, 'PRI')
        self.assertEqual(self.club2.genre, 'Fiction')
        self.assertEqual(self.club2.description, 'description')

    def test_succesful_club3_update(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url3, self.form_input_in_person_private, follow=True)
        after_count = Club.objects.count()
        self.user.refresh_from_db()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_feed', kwargs={'club_name': 'club1'})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        # response = self.client.post(self.url, self.form_input_online_public)
        self.assertTemplateUsed(response, 'club_feed.html')
        self.club3 = Club.objects.get(club_name='club1')
        self.assertEqual(self.club3.meeting_status, 'OFF')
        self.assertEqual(self.club3.city, 'city1')
        self.assertEqual(self.club3.country, 'country1')
        self.assertEqual(self.club3.location, 'location')
        self.assertEqual(self.club3.public_status, 'PRI')
        self.assertEqual(self.club3.genre, 'Fiction')
        self.assertEqual(self.club3.description, 'description')

    def test_succesful_club3_update(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url3, self.form_input_in_person_public, follow=True)
        after_count = Club.objects.count()
        self.user.refresh_from_db()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_feed', kwargs={'club_name': 'club1'})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        # response = self.client.post(self.url, self.form_input_online_public)
        self.assertTemplateUsed(response, 'club_feed.html')
        self.club3 = Club.objects.get(club_name='club1')
        self.assertEqual(self.club3.meeting_status, 'OFF')
        self.assertEqual(self.club3.city, 'city1')
        self.assertEqual(self.club3.country, 'country1')
        self.assertEqual(self.club3.location, 'location')
        self.assertEqual(self.club3.public_status, 'PUB')
        self.assertEqual(self.club3.genre, 'Non-Fiction')
        self.assertEqual(self.club3.description, 'description')


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

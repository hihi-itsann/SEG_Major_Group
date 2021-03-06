from django.test import TestCase
from django.urls import reverse

from bookclubs.forms import ClubForm
from bookclubs.models import Club, User, Book


class CreateClubViewTestCase(TestCase):
    """Tests for the creation of a club"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN="0195153448")
        self.url = reverse('create_club')
        self.form_input_online_public = {
            'club_name': 'club1',
            'meeting_status': 'ONL',
            'location': 'location',
            'city': 'city1',
            'country': 'country1',
            'public_status': 'PUB',
            'genre': 'Non-Fiction',
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
            'genre': 'Non-Fiction',
            'description': 'description',
        }

    def test_create_club_url(self):
        self.assertEqual(self.url, '/create_club/')

    def test_get_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))

    def test_unsuccessful_online_public_create_club(self):
        self.form_input_online_public['club_name'] = ''
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input_online_public, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response = self.client.post(self.url, self.form_input_online_public)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))

    def test_successful_online_public_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input_online_public, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('club_feed', kwargs={'club_name': 'club1'})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        # response = self.client.post(self.url, self.form_input_online_public)
        self.assertTemplateUsed(response, 'club_feed.html')
        club = Club.objects.get(club_name='club1')
        self.assertEqual(club.meeting_status, 'ONL')
        # self.assertEqual(club.city, 'city1')
        # self.assertEqual(club.country, 'country1')
        self.assertEqual(club.location, 'location')
        self.assertEqual(club.public_status, 'PUB')
        self.assertEqual(club.genre, 'Non-Fiction')
        self.assertEqual(club.description, 'description')

    def test_unsuccessful_online_private_create_club(self):
        self.form_input_online_private['club_name'] = ''
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input_online_private, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response = self.client.post(self.url, self.form_input_online_private)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))

    def test_successful_online_private_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input_online_private, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('club_feed', kwargs={'club_name': 'club1'})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        # response = self.client.post(self.url, self.form_input_online_public)
        self.assertTemplateUsed(response, 'club_feed.html')
        club = Club.objects.get(club_name='club1')
        self.assertEqual(club.meeting_status, 'ONL')
        # self.assertEqual(club.city, 'city1')
        # self.assertEqual(club.country, 'country1')
        self.assertEqual(club.location, 'location')
        self.assertEqual(club.public_status, 'PRI')
        self.assertEqual(club.genre, 'Fiction')
        self.assertEqual(club.description, 'description')

    def test_unsuccessful_in_person_private_create_club(self):
        self.form_input_in_person_private['club_name'] = ''
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input_in_person_private, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response = self.client.post(self.url, self.form_input_in_person_private)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))

    def test_successful_in_person_private_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input_in_person_private, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('club_feed', kwargs={'club_name': 'club1'})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        # response = self.client.post(self.url, self.form_input_online_public)
        self.assertTemplateUsed(response, 'club_feed.html')
        club = Club.objects.get(club_name='club1')
        self.assertEqual(club.meeting_status, 'OFF')
        # self.assertEqual(club.city, 'city1')
        # self.assertEqual(club.country, 'country1')
        self.assertEqual(club.location, 'location')
        self.assertEqual(club.public_status, 'PRI')
        self.assertEqual(club.genre, 'Fiction')
        self.assertEqual(club.description, 'description')

    def test_unsuccessful_in_person_public_create_club(self):
        self.form_input_in_person_public['club_name'] = ''
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input_in_person_public, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response = self.client.post(self.url, self.form_input_in_person_public)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))

    def test_successful_in_person_public_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input_in_person_public, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('club_feed', kwargs={'club_name': 'club1'})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        # response = self.client.post(self.url, self.form_input_online_public)
        self.assertTemplateUsed(response, 'club_feed.html')
        club = Club.objects.get(club_name='club1')
        self.assertEqual(club.meeting_status, 'OFF')
        # self.assertEqual(club.city, 'city1')
        # self.assertEqual(club.country, 'country1')
        self.assertEqual(club.location, 'location')
        self.assertEqual(club.public_status, 'PUB')
        self.assertEqual(club.genre, 'Non-Fiction')
        self.assertEqual(club.description, 'description')

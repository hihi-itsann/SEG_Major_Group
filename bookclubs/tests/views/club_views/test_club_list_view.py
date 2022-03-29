from django.test import TestCase
from django.urls import reverse
from bookclubs.models import User, Club, Role
from bookclubs.tests.helpers import reverse_with_next


class ClubListViewTest(TestCase):
    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.url = reverse('club_list')
        self.user = User.objects.get(username='@johndoe')
        self._create_test_clubs()

    def test_club_list_url(self):
        self.assertEqual(self.url, '/club_list/')

    def test_get_club_list(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), 5)
        for club_id in range(9):
            if club_id % 2 == 0:
                club = Club.objects.get(club_name=f'name{club_id}')
                club_url = reverse('create_application', kwargs={'club_name': club.club_name})
                self.assertContains(response, club_url)

    def test_get_club_list_with_PUB_public_status(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('club_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), 5)
        self.assertEqual(response.context['club_count'], 9)
        self.assertQuerysetEqual(Club.objects.filter(public_status='PUB').filter(meeting_status='ONL'),
                                 response.context['clubs'], ordered=False)
        for club_id in range(9):
            if club_id % 2 == 0:
                club = Club.objects.get(club_name=f'name{club_id}')
                club_url = reverse('create_application', kwargs={'club_name': club.club_name})
                self.assertContains(response, club_url)

    def test_get_club_list_with_ONL_meeting_status(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('club_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), 5)
        self.assertEqual(response.context['meeting_status'], 'Online')
        self.assertQuerysetEqual(Club.objects.filter(meeting_status='ONL'), response.context['clubs'], ordered=False)
        for club_id in range(9):
            if club_id % 2 == 0:
                club = Club.objects.get(club_name=f'name{club_id}')
                club_url = reverse('create_application', kwargs={'club_name': club.club_name})
                self.assertContains(response, club_url)

    def test_get_club_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_club_list_with_in_person_meeting_status_and_same_city_distance(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('club_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clubs']), 5)
        self.assertEqual(response.context['club_count'], 9)
        form_input = {'meeting_status': 'In person', 'distance': 'same city'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(len(response.context['clubs']), 4)
        self.assertEqual(response.context['club_count'], 9)
        self.assertEqual(response.context['is_suitable_clubs'], True)
        self.assertEqual(response.context['distance'], 'same city')
        self.assertQuerysetEqual(Club.objects.filter(meeting_status='OFF'), response.context['clubs'], ordered=False)

        for club_id in range(9):
            if club_id % 2 != 0:
                club = Club.objects.get(club_name=f'name{club_id}')
                club_url = reverse('create_application', kwargs={'club_name': club.club_name})
                self.assertContains(response, club_url)

    def test_get_club_list_with_in_person_meeting_status_and_same_country_distance(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('club_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clubs']), 5)
        self.assertEqual(response.context['club_count'], 9)
        form_input = {'meeting_status': 'In person', 'distance': 'same country'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(len(response.context['clubs']), 0)
        self.assertEqual(response.context['club_count'], 9)
        self.assertEqual(response.context['is_suitable_clubs'], False)
        self.assertEqual(response.context['distance'], 'same country')
        self.assertQuerysetEqual(Club.objects.filter(meeting_status='OFF').filter(country='UK'),
                                 response.context['clubs'], ordered=False)

    def test_club_list_does_not_show_club_user_is_in(self):
        club_one = Club.objects.get(id=1)
        Role.objects.create(user=self.user, club=club_one, club_role='MEM')
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clubs']), 4)
        self.assertNotIn(club_one, response.context['clubs'])

    def _create_test_clubs(self, club_count=9):
        for club_id in range(club_count):
            if club_id % 2 == 0:
                Club.objects.create(
                    club_name=f'name{club_id}',
                    description=f'title{club_id}',
                    meeting_status='ONL',
                    location=f'LOCATION{club_id}',
                    city=f'city{club_id}',
                    country=f'country{club_id}',
                    public_status='PUB'
                )
            else:
                Club.objects.create(
                    club_name=f'name{club_id}',
                    description=f'title{club_id}',
                    meeting_status='OFF',
                    location=f'LOCATION{club_id}',
                    city="London",
                    country=f'country{club_id}',
                    public_status='PUB'
                )

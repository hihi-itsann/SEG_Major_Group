from django.test import TestCase
from django.urls import reverse

from bookclubs.models import User, Book, Club, Role
from bookclubs.tests.helpers import reverse_with_next


class ShowBookRecommendationsViewTestCase(TestCase):
    VIEW = 'show_book_recommendations'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
        'bookclubs/tests/fixtures/default_book.json',
        'bookclubs/tests/fixtures/other_books.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.another_book = Book.objects.get(ISBN='0002005018')
        self.club = Club.objects.get(club_name='private_online')
        self.url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name})

    def log_in(self, user):
        self.client.login(username=user.username, password="Password123")

    def test_show_book_recommendations_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_name}/meeting/show_books/')

    def test_show_book_recommendations_with_invalid_club(self):
        self.log_in(self.user)
        url = reverse(self.VIEW, kwargs={'club_name': 'invalid'})
        redirect_url = reverse('feed')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_book_recommendations_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_book_recommendations_redirects_when_not_a_member(self):
        self.log_in(self.user)
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_book_recommendations_successful_under_ten_books(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club, club_role='MEM')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_book_recommendations.html')
        self.assertContains(response, "Recommended Books")
        self.assertContains(response, "Classical Mythology")

    def test_get_show_book_recommendations_successful_over_ten_books(self):
        self.log_in(self.user)
        list_of_isbn = ['0060973129', '0374157065', '0393045218', '0399135782', '0425176428', '0671870432',
                        '0679425608', '074322678X', '0771074670', '080652121X']
        for isbn in list_of_isbn:
            Book.objects.create(ISBN=isbn, title=f'Test Book {isbn}',
                                author='Test', year_of_publication=2022,
                                publisher='Test', image_url_s='No Image',
                                image_url_m='No Image', image_url_l='No Image')
        Role.objects.create(user=self.user, club=self.club, club_role='MEM')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_book_recommendations.html')
        self.assertContains(response, "Recommended Books")
        self.assertContains(response, "Test Book")

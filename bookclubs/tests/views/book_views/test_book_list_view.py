from django.test import TestCase
from django.urls import reverse

from bookclubs.models import User, Book
from bookclubs.tests.helpers import reverse_with_next


class BookListViewTest(TestCase):
    """Tests for showing the book list"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.url = reverse('book_list', kwargs={'book_genre': 'All'})
        self.user = User.objects.get(username='@johndoe')
        self._create_test_books(9)

    def test_book_list_url(self):
        self.assertEqual(self.url, '/book_list/All/')

    def test_get_book_list(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_list.html')
        self.assertEqual(len(response.context['books']), 9)
        for book_id in range(9):
            book = Book.objects.get(ISBN=f'XXXXXXXXX{book_id}')
            book_url = reverse('show_book', kwargs={'ISBN': book.pk})
            self.assertContains(response, book_url)

    def test_get_book_list_with_Fiction_genre(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('book_list', kwargs={'book_genre': 'Fiction'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_list.html')
        self.assertEqual(len(response.context['books']), 9)
        self.assertQuerysetEqual(Book.objects.filter(genre='Fiction'), response.context['books'])
        for book_id in range(9):
            book = Book.objects.get(ISBN=f'XXXXXXXXX{book_id}')
            book_url = reverse('show_book', kwargs={'ISBN': book.pk})
            self.assertContains(response, book_url)

    def test_get_book_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_test_books(self, book_count=9):
        for book_id in range(book_count):
            Book.objects.create(
                ISBN=f'XXXXXXXXX{book_id}',
                title=f'title{book_id}',
                author=f'author{book_id}',
                year_of_publication=book_id + 1000,
                publisher=f'Last{book_id}',
                image_url_s=f'url-s{book_id}',
                image_url_m=f'url-m{book_id}',
                image_url_l=f'url-l{book_id}',
                genre="Fiction"
            )

from django.test import TestCase
from django.urls import reverse
from bookclubs.models import Post, User, Book, BookStatus
from bookclubs.tests.helpers import reverse_with_next


class CreateBookStatusTest(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.url = reverse('create_book_status', kwargs={'ISBN': self.book.ISBN})

    def test_create_book_status_url(self):
        self.assertEqual(self.url, f'/create_book_status/{self.book.ISBN}/')

    def test_create_book_status_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_create_book_status(self):
        self.client.login(username=self.user.username, password="Password123")
        book_status_count_before = BookStatus.objects.count()
        response = self.client.post(self.url, follow=True)
        book_status_count_after = BookStatus.objects.count()
        self.assertEqual(book_status_count_after, book_status_count_before+1)
        response_url = reverse('reading_book_list', kwargs={'book_genre': 'All'})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'reading_book_list.html')

    def test_unsuccessful_create_book_status_when_book_status_is_already_exist(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url, follow=True)
        book_status_count_before = BookStatus.objects.count()
        response = self.client.post(self.url)
        book_status_count_after = BookStatus.objects.count()
        self.assertEqual(book_status_count_after, book_status_count_before)
        response_url = reverse('show_book', kwargs={'ISBN': self.book.ISBN})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )

    def test_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

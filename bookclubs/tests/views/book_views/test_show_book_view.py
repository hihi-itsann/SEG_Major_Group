from django.test import TestCase
from django.urls import reverse
from bookclubs.models import User, Book, BookStatus
from bookclubs.tests.helpers import reverse_with_next


class ShowBookViewTestCase(TestCase):

    VIEW = 'show_book'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json',
        'bookclubs/tests/fixtures/other_books.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.target_book = Book.objects.get(ISBN='0002005018')
        self.book_status = BookStatus.objects.create(
            book=self.target_book,
            user=self.user,
            status='U'
        )
        self.url = reverse(self.VIEW, kwargs={'ISBN': self.target_book.ISBN})

    def test_show_book_url(self):
        self.assertEqual(self.url, f'/book/{self.target_book.ISBN}/')

    def test_get_show_book_with_valid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        self.assertContains(response, "0002005018")
        self.assertContains(response, "Clara Callan")
        reading_status = response.context['readingStatus']
        self.assertEqual(reading_status, 'U')

    def test_get_show_book_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_book', kwargs={'ISBN': 'invalid_ISBN'})
        response = self.client.get(url, follow=True)
        response_url = reverse('book_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'book_list.html')

    def test_get_show_book_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

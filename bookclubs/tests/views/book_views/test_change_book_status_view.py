from django.test import TestCase
from django.urls import reverse

from bookclubs.models import User, Book, BookStatus
from bookclubs.tests.helpers import reverse_with_next


class ChangeBookStatusViewTestCase(TestCase):
    """Tests for changing book reading status"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.book_status = BookStatus.objects.create(
            book=self.book,
            user=self.user,
            status='U'
        )
        self.choice = 'F'
        self.url = reverse('change_book_status', kwargs={'ISBN': self.book.ISBN, 'choice': self.choice})

    def test_change_book_status_url(self):
        self.assertEqual(self.url, f'/change_book_status/{self.book.ISBN}/{self.choice}/')

    def test_change_book_status_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_change_book_status_is_successful(self):
        self.client.login(username=self.user.username, password="Password123")
        status_before = self.book_status.status
        self.assertEqual(status_before, 'U')
        response = self.client.post(self.url, follow=True)
        status_after = BookStatus.objects.get(user=self.user, book=self.book).status
        self.assertEqual(status_after, 'F')
        self.assertNotEqual(status_before, status_after)
        response_url = reverse('show_book',kwargs={'ISBN': self.book.ISBN})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_change_book_status_is_unsuccessful_when_choice_is_invalid(self):
        self.client.login(username=self.user.username, password="Password123")
        status_before = self.book_status.status
        self.assertEqual(status_before, 'U')
        url=f'/change_book_status/{self.book.ISBN}/A/'
        response = self.client.post(url, follow=True)
        status_after = BookStatus.objects.get(user=self.user, book=self.book).status
        self.assertNotEqual(status_after, 'F')
        self.assertEqual(status_after, 'U')
        self.assertEqual(status_before, status_after)
        response_url = reverse('show_book',kwargs={'ISBN': self.book.ISBN})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

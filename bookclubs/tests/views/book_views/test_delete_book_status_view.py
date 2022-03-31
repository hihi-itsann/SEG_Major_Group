from django.contrib import messages
from django.test import TestCase
from django.urls import reverse

from bookclubs.models import User, Book, BookStatus
from bookclubs.tests.helpers import reverse_with_next


class DeleteBookStatusTest(TestCase):
    """Tests for the deletion of a book status"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.bookStatus = BookStatus.objects.create(
            book=self.book,
            user=self.user,
            status='U'
        )
        self.url = reverse('delete_book_status', kwargs={'ISBN': self.book.ISBN})

    def test_delete_book_status_url(self):
        self.assertEqual(self.url, f'/delete_book_status/{self.book.ISBN}/')

    def test_delete_book_status_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_delete_comment(self):
        self.client.login(username=self.user.username, password="Password123")
        book_status_count_before = BookStatus.objects.count()
        response = self.client.delete(self.url)
        book_status_count_after = BookStatus.objects.count()
        self.assertEqual(book_status_count_after, book_status_count_before - 1)
        response_url = reverse('reading_book_list', kwargs={'book_genre': 'All'})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )

    def test_unsuccessful_delete_book_status_when_book_status_is_not_in_reading_list(self):
        self.client.login(username=self.other_user.username, password='Password123')
        book_status_count_before = BookStatus.objects.count()
        response = self.client.delete(self.url, follow=True)
        book_status_count_after = BookStatus.objects.count()
        self.assertEqual(book_status_count_after, book_status_count_before)
        response_url = reverse('show_book', kwargs={'ISBN': self.book.ISBN})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

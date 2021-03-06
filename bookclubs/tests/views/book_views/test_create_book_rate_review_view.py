from django.test import TestCase
from django.urls import reverse

from bookclubs.forms import RateReviewForm
from bookclubs.models import User, Book, BookStatus, BookRatingReview
from bookclubs.tests.helpers import reverse_with_next


class CreateBookRateViewTestCase(TestCase):
    """Tests for the create book rate view."""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.form_input = {
            'rate': 9,
            'user': self.user,
            'book': self.book,
            'review': 'this is a review.'
        }
        self.bookStatus = BookStatus.objects.create(
            user=self.user,
            book=self.book,
            status='F'
        )
        self.url = reverse('create_book_rating_review', kwargs={'ISBN': self.book.ISBN})

    def test_get_create_book_url(self):
        self.assertEqual(self.url, f'/create_book_rating_review/{self.book.ISBN}/')

    def test_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_create_book_review(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_book', kwargs={'ISBN': self.book.ISBN})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_book.html')
        self.assertContains(response, self.book.title)
        self.assertEqual(response.context['book'], self.book)
        form = response.context['form']
        self.assertTrue(isinstance(form, RateReviewForm))
        self.assertFalse(form.is_bound)

    def test_successful_create(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = BookRatingReview.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = BookRatingReview.objects.count()
        self.assertEqual(after_count, before_count + 1)
        book = Book.objects.get(ISBN='0195153448')
        self.assertTemplateUsed(response, 'show_book.html')
        response_url = '{}#education'.format(reverse('show_book', kwargs={'ISBN': self.book.ISBN}))
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

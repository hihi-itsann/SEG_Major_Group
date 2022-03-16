from django.test import TestCase
from django.urls import reverse
from bookclubs.forms import RateReviewForm
from bookclubs.models import User, Book, BookStatus, BookRatingReview
from bookclubs.tests.helpers import reverse_with_next


class DeleteBookRateViewTestCase(TestCase):
    """Tests of the delete book rate review view."""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.book_rating_review = BookRatingReview.objects.create(
            user=self.user,
            book=self.book,
            rate=9,
            review='this is a review.'
        )
        self.url = reverse('delete_book_rating_review', kwargs={'ISBN': self.book.ISBN, 'pk': self.book_rating_review.id})

    def test_delete_rating_review_url(self):
        self.assertEqual(self.url, f'/delete_book_rating_review/{self.book.ISBN}/{self.book_rating_review.id}/')

    def test_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_delete_rating_review(self):
        self.client.login(username=self.user.username, password="Password123")
        rating_review_count_before = BookRatingReview.objects.count()
        response = self.client.delete(self.url)
        rating_review_count_after = BookRatingReview.objects.count()
        self.assertEqual(rating_review_count_after, rating_review_count_before-1)
        response_url = reverse('show_book', kwargs={'ISBN': self.book.ISBN})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )

    def test_unsuccessful_delete_rating_review_when_does_not_exist(self):
        self.client.login(username=self.other_user.username, password='Password123')
        book_feedback_count_before = BookRatingReview.objects.count()
        response = self.client.delete(self.url, follow=True)
        book_feedback_count_after = BookRatingReview.objects.count()
        self.assertEqual(book_feedback_count_after, book_feedback_count_before)
        response_url = reverse('show_book', kwargs={'ISBN': self.book.ISBN})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )

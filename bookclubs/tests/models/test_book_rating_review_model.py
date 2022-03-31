from django.core.exceptions import ValidationError
from django.test import TestCase

from bookclubs.models import User, BookRatingReview, Book


class BookRatingReviewModelTestCase(TestCase):
    """Unit tests for the BookRatingReview model"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.rating_review = BookRatingReview(
            rate=9,
            user=self.user,
            book=self.book,
            review='this is a book review.'
        )

    def test_get_book(self):
        self.assertEqual(self.rating_review.book, self.book)

    def test_get_user(self):
        self.assertEqual(self.rating_review.user, self.user)

    def _assert_rating_review_is_valid(self):
        self.rating_review.full_clean()

    def _assert_rating_review_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.rating_review.full_clean()

    def test_valid_rating_review(self):
        self._assert_rating_review_is_valid()

    def test_user_must_not_be_blank(self):
        self.rating_review.user = None
        self._assert_rating_review_is_invalid()

    def test_book_must_not_be_blank(self):
        self.rating_review.book = None
        self._assert_rating_review_is_invalid()

    def test_rate_must_not_be_blank(self):
        self.rating_review.rate = ''
        self._assert_rating_review_is_invalid()

    def test_rate_can_be_0(self):
        self.rating_review.rate = 0
        self._assert_rating_review_is_valid()

    def test_rate_cannot_be_negative(self):
        self.rating_review.rate = -1
        self._assert_rating_review_is_invalid()

    def test_rate_can_be_10(self):
        self.rating_review.rate = 0
        self._assert_rating_review_is_valid()

    def test_rate_cannot_be_11(self):
        self.rating_review.rate = 11
        self._assert_rating_review_is_invalid()

    def test_review_can_be_blank(self):
        self.rating_review.review = ''
        self._assert_rating_review_is_valid()

    def test_review_must_not_be_overlong(self):
        self.rating_review.review = 'x' * 521
        self._assert_rating_review_is_invalid()

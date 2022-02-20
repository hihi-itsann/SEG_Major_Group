from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Rating, Book

class RatingModelTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.rating = Rating(
            rate=9,
            user=self.user,
            book=self.book
        )

    def test_get_book(self):
       self.assertEqual(self.rating.book, self.book)

    def test_get_user(self):
       self.assertEqual(self.rating.user, self.user)

    def _assert_rating_is_valid(self):
        self.rating.full_clean()

    def _assert_rating_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.rating.full_clean()

    def test_valid_rating(self):
        self._assert_rating_is_valid()

    def test_user_must_not_be_blank(self):
        self.rating.user = None
        self._assert_rating_is_invalid()

    def test_book_must_not_be_blank(self):
        self.rating.book = None
        self._assert_rating_is_invalid()

    def test_rate_must_not_be_blank(self):
        self.rating.rate = ''
        self._assert_rating_is_invalid()

    def test_rate_can_be_0(self):
        self.rating.rate = 0
        self._assert_rating_is_valid()

    def test_rate_cannot_be_negative(self):
        self.rating.rate = -1
        self._assert_rating_is_invalid()

    def test_rate_can_be_10(self):
        self.rating.rate = 0
        self._assert_rating_is_valid()

    def test_rate_cannot_be_11(self):
        self.rating.rate = 11
        self._assert_rating_is_invalid()

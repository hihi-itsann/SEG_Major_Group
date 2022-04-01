from django.core.exceptions import ValidationError
from django.test import TestCase

from bookclubs.models import User, Book, BookStatus


class BookStatusModelTestCase(TestCase):
    """Unit tests for the BookStatus model"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json',
        'bookclubs/tests/fixtures/other_books.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.book_status = BookStatus.objects.create(
            book=self.book,
            user=self.user,
            status='U'
        )

    def _assert_book_status_is_valid(self):
        self.book_status.full_clean()

    def _assert_book_status_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.book_status.full_clean()

    def test_valid_book_status(self):
        self._assert_book_status_is_valid()

    def test_user_must_not_be_blank(self):
        self.book_status.user = None
        self._assert_book_status_is_invalid()

    def test_book_must_not_be_blank(self):
        self.book_status.book = None
        self._assert_book_status_is_invalid()

    def test_status_can_not_be_blank(self):
        self.book_status.status = ''
        self._assert_book_status_is_invalid()

    def test_status_need_not_be_unique(self):
        second_book = Book.objects.get(ISBN='0002005018')
        second_book_status = BookStatus.objects.create(
            book=second_book,
            user=self.user,
            status='U'
        )
        self.book_status.status = second_book_status.status
        self._assert_book_status_is_valid()

    def test_status_may_contain_1_characters(self):
        self.book_status.status = 'U' * 1
        self._assert_book_status_is_valid()

    def test_status_must_not_contain_more_than_1_characters_long(self):
        self.book_status.status = 'U' * 2
        self._assert_book_status_is_invalid()

    def test_status_must_be_chose_from_list(self):
        self.book_status.status = 'U'
        self._assert_book_status_is_valid()
        self.book_status.status = 'R'
        self._assert_book_status_is_valid()
        self.book_status.status = 'F'
        self._assert_book_status_is_valid()
        self.book_status.status = 'A'
        self._assert_book_status_is_invalid()
        self.book_status.status = 'B'
        self._assert_book_status_is_invalid()

    # Method tests

    def test_change_status_unread(self):
        """Test change_status (to unread) method"""
        self.book_status.change_status('U')
        self.book_status.refresh_from_db()
        self.assertEqual(self.book_status.status, 'U')

    def test_change_status_reading(self):
        """Test change_status (to reading) method"""
        self.book_status.change_status('R')
        self.book_status.refresh_from_db()
        self.assertEqual(self.book_status.status, 'R')

    def test_change_status_finished(self):
        """Test change_status (to finished) method"""
        self.book_status.change_status('F')
        self.book_status.refresh_from_db()
        self.assertEqual(self.book_status.status, 'F')

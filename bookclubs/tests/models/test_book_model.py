from django.core.exceptions import ValidationError
from django.test import TestCase
from libgravatar import Gravatar

from bookclubs.models import Book


class BookModelTestCase(TestCase):
    fixtures = [
        'bookclubs/tests/fixtures/default_book.json',
        'bookclubs/tests/fixtures/other_books.json'
    ]

    def setUp(self):
        self.book = Book.objects.get(ISBN='0195153448')

    def _assert_book_is_valid(self):
        self.book.full_clean()

    def _assert_book_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.book.full_clean()

    def test_get_isbn(self):
        (self.book.get_ISBN(), '0195153448')

    def test_valid_book(self):
        self._assert_book_is_valid()

    def test_title_cannot_be_blank(self):
        self.book.title = ''
        self._assert_book_is_invalid()

    def test_author_cannot_be_blank(self):
        self.book.author = ''
        self._assert_book_is_invalid()

    def test_year_of_publication_cannot_be_blank(self):
        self.book.year_of_publication = ''
        self._assert_book_is_invalid()

    def test_publisher_cannot_be_blank(self):
        self.book.publisher = ''
        self._assert_book_is_invalid()

    def test_image_url_s_cannot_be_blank(self):
        self.book.image_url_s = ''
        self._assert_book_is_invalid()

    def test_image_url_m_cannot_be_blank(self):
        self.book.image_url_m = ''
        self._assert_book_is_invalid()

    def test_image_url_l_cannot_be_blank(self):
        self.book.image_url_l = ''
        self._assert_book_is_invalid()

    def test_title_can_be_100_characters_long(self):
        self.book.title = 'X' * 100
        self._assert_book_is_valid()

    def test_title_cannot_be_over_100_characters_long(self):
        self.book.title = 'X' * 101
        self._assert_book_is_invalid()

    def test_author_can_be_100_characters_long(self):
        self.book.author = 'X' * 100
        self._assert_book_is_valid()

    def test_author_cannot_be_over_100_characters_long(self):
        self.book.author = 'X' * 101
        self._assert_book_is_invalid()

    def test_year_of_publication_can_be_2022(self):
        self.book.year_of_publication = 2022
        self._assert_book_is_valid()

    def test_year_of_publication_cannot_be_2023(self):
        self.book.year_of_publication = 2023
        self._assert_book_is_invalid()

    def test_year_of_publication_can_be_1000(self):
        self.book.year_of_publication = 1000
        self._assert_book_is_valid()

    def test_year_of_publication_cannot_be_999(self):
        self.book.year_of_publication = 999
        self._assert_book_is_invalid()

    def test_publisher_can_be_100_characters_long(self):
        self.book.publisher = 'X' * 100
        self._assert_book_is_valid()

    def test_publisher_cannot_be_over_100_characters_long(self):
        self.book.publisher = 'X' * 101
        self._assert_book_is_invalid()

    def test_ISBN_must_be_unique(self):
        second_book = Book.objects.get(ISBN='0002005018')
        self.book.ISBN = second_book.ISBN
        self._assert_book_is_invalid()

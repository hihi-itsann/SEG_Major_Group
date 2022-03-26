from django.test import TestCase
from bookclubs.models import Book
from django.db.utils import OperationalError


class GetGenresStaticMethodTestCase(TestCase):
    """Tests Book.get_genre(), but doesn't show in coverage as can't assert if a print statement to the terminal"""

    fixtures = [
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def test_get_genre_when_no_books(self):
        Book.objects.get(ISBN='0195153448').delete()
        self.assertIn(('Fiction', 'Fiction'), Book.get_genres())
        self.assertIn(('Non-Fiction', 'Non-Fiction'), Book.get_genres())
        self.assertNotIn(('Social Science', 'Social Science'), Book.get_genres())

    def test_get_genre_when_one_book(self):
        Book.objects.get(ISBN='0195153448')
        self.assertIn(('Social Science', 'Social Science'), Book.get_genres())
        self.assertIn(('Fiction', 'Fiction'), Book.get_genres())
        self.assertIn(('Non-Fiction', 'Non-Fiction'), Book.get_genres())


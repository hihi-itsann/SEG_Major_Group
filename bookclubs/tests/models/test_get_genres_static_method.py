from django.test import TestCase

from bookclubs.models import Book


class GetGenresStaticMethodTestCase(TestCase):
    """Unit tests Book.get_genre, but doesn't show in coverage as can't assert if a print statement to the terminal"""

    fixtures = [
        'bookclubs/tests/fixtures/default_book.json',
    ]

    # Method tests

    def test_get_genre_when_no_books(self):
        """Test get_genre when there are no books in the system, but cannot assert print statement"""
        Book.objects.get(ISBN='0195153448').delete()
        self.assertIn(('Fiction', 'Fiction'), Book.get_genres())
        self.assertIn(('Non-Fiction', 'Non-Fiction'), Book.get_genres())
        self.assertNotIn(('Social Science', 'Social Science'), Book.get_genres())

    def test_get_genre_when_one_book(self):
        """Test get_genre when there is a book in the system"""
        Book.objects.get(ISBN='0195153448')
        self.assertIn(('Social Science', 'Social Science'), Book.get_genres())
        self.assertIn(('Fiction', 'Fiction'), Book.get_genres())
        self.assertIn(('Non-Fiction', 'Non-Fiction'), Book.get_genres())

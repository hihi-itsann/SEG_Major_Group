from django.test import TestCase

from bookclubs.models import Club, Book, ClubBookAverageRating


class ClubBookAverageRatingModelMethodsTestCase(TestCase):
    """Unit tests for the methods in the ClubBookAverageRating model"""

    fixtures = [
        'bookclubs/tests/fixtures/default_clubs.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(club_name='private_online')
        self.book = Book.objects.get(ISBN='0195153448')
        self.club_book_average_rating = ClubBookAverageRating.objects.create(
            club=self.club,
            book=self.book,
            rate=0,
            number_of_ratings=0
        )

    # Method tests

    def test_add_rating(self):
        """Test add_rating method"""
        self.club_book_average_rating.add_rating(10)
        self.club_book_average_rating.refresh_from_db()
        self.assertEqual(self.club_book_average_rating.rate, 10)
        self.club_book_average_rating.add_rating(5)
        self.club_book_average_rating.refresh_from_db()
        self.assertEqual(self.club_book_average_rating.rate, 15)

    def test_increment_number_of_ratings(self):
        """Test increment_number_of_ratings method"""
        self.club_book_average_rating.increment_number_of_ratings()
        self.club_book_average_rating.refresh_from_db()
        self.assertEqual(self.club_book_average_rating.number_of_ratings, 1)
        self.club_book_average_rating.increment_number_of_ratings()
        self.club_book_average_rating.refresh_from_db()
        self.assertEqual(self.club_book_average_rating.number_of_ratings, 2)

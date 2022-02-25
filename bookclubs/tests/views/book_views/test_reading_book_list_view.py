from django.test import TestCase
from django.urls import reverse
from bookclubs.models import User, Book, BookStatus
from bookclubs.tests.helpers import reverse_with_next

class BookListViewTest(TestCase):
    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        self.book = Book.objects.get(ISBN='0195153448')
        # self.url = reverse('reading_book_list', kwargs={'book_genra': self.book.genra})
        self.url = reverse('reading_book_list', kwargs={'book_genra': 'All'})
        self.user = User.objects.get(username='@johndoe')

    def test_reading_book_list_url(self):
        self.assertEqual(self.url,f'/reading_book_list/All/')

    def test_get_reading_book_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_reading_books(3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_book_list.html')
        self.assertEqual(len(response.context['unreadBooks']), 3)
        self.assertEqual(len(response.context['readingBooks']), 3)
        self.assertEqual(len(response.context['finishedBooks']), 3)
        for book_id in range(3):
            book = Book.objects.get(ISBN=f'XXXXXXXXX{book_id}')
            book_url = reverse('show_book', kwargs={'ISBN': book.ISBN})
            self.assertContains(response, book_url)
        for book_id in range(3):
            book = Book.objects.get(ISBN=f'YYYYYYYYY{book_id}')
            book_url = reverse('show_book', kwargs={'ISBN': book.ISBN})
            self.assertContains(response, book_url)
        for book_id in range(3):
            book = Book.objects.get(ISBN=f'ZZZZZZZZZ{book_id}')
            book_url = reverse('show_book', kwargs={'ISBN': book.ISBN})
            self.assertContains(response, book_url)

    def test_get_book_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_reading_books(self, book_count=3):
        for book_id in range(book_count):
            unreadBook = Book.objects.create(
                ISBN=f'XXXXXXXXX{book_id}',
                title=f'unreadBooktitle{book_id}',
                author=f'author{book_id}',
                year_of_publication=book_id+1000,
                publisher=f'Last{book_id}',
                image_url_s=f'url-s{book_id}',
                image_url_m=f'url-m{book_id}',
                image_url_l=f'url-l{book_id}',
                genra="Social Science"
            )
            BookStatus.objects.create(
                book=unreadBook,
                user=self.user
            )

            readingBook = Book.objects.create(
                ISBN=f'YYYYYYYYY{book_id}',
                title=f'readingBooktitle{book_id}',
                author=f'author{book_id}',
                year_of_publication=book_id+1000,
                publisher=f'Last{book_id}',
                image_url_s=f'url-s{book_id}',
                image_url_m=f'url-m{book_id}',
                image_url_l=f'url-l{book_id}',
                genra="Fiction"
            )
            BookStatus.objects.create(
                book=readingBook,
                user=self.user,
                status='R'
            )

            finishedBook = Book.objects.create(
                ISBN=f'ZZZZZZZZZ{book_id}',
                title=f'finishedBooktitle{book_id}',
                author=f'author{book_id}',
                year_of_publication=book_id+1000,
                publisher=f'Last{book_id}',
                image_url_s=f'url-s{book_id}',
                image_url_m=f'url-m{book_id}',
                image_url_l=f'url-l{book_id}',
                genra="Medical"
            )
            BookStatus.objects.create(
                book=finishedBook,
                user=self.user,
                status='F'
            )

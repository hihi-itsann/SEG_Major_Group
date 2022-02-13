from django.test import TestCase
from django.urls import reverse
from bookclubs.forms import RateForm
from bookclubs.models import User, Book, Rating

class CreateBookRateViewTestCase(TestCase):
    """Tests of the create book rate view."""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.form_input = {
            'rate':9,
            'user':self.user,
            'book':self.book
        }
        self.url = reverse('create_book_rating', kwargs={'ISBN': self.book.ISBN})

    def test_get_create_book_url(self):
        self.assertEqual(self.url,f'/create_book_rating/{self.book.ISBN}/')

    def test_get_create_book(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_book_rating.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RateForm))
        self.assertFalse(form.is_bound)

    def test_succesful_create(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Rating.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Rating.objects.count()
        self.assertEqual(after_count, before_count+1)
        book = Book.objects.get(ISBN='0195153448')
        self.assertTemplateUsed(response, 'book_list.html')

from django.test import TestCase
from django.contrib.auth.hashers import check_password
from bookclubs.forms import ClubForm
from django.urls import reverse
from bookclubs.models import Club, User, Book
from bookclubs.tests.helpers import reverse_with_next

class UpdateClubViewTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_book.json',
        'bookclubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(ISBN="0195153448")
        self.club1 =  Club.objects.get(club_name='private_online')
        self.club2 =  Club.objects.get(club_name='public_online')
        self.club3 =  Club.objects.get(club_name='private_in-person')
        self.club4 =  Club.objects.get(club_name='public_in-person')

        self.url1 = reverse('update_club_info',kwargs={'club_name':self.club1.club_name})
        self.url2 = reverse('update_club_info',kwargs={'club_name':self.club2.club_name})
        self.url3 = reverse('update_club_info',kwargs={'club_name':self.club3.club_name})
        self.url4 = reverse('update_club_info',kwargs={'club_name':self.club4.club_name})

    def test_create_club_url(self):
        self.assertEqual(reverse('update_club_info',kwargs={'club_name':self.club1.club_name}), f'/club/{self.club1.club_name}/update_club_info/')
        self.assertEqual(reverse('update_club_info',kwargs={'club_name':self.club2.club_name}), f'/club/{self.club2.club_name}/update_club_info/')
        self.assertEqual(reverse('update_club_info',kwargs={'club_name':self.club3.club_name}), f'/club/{self.club3.club_name}/update_club_info/')
        self.assertEqual(reverse('update_club_info',kwargs={'club_name':self.club4.club_name}), f'/club/{self.club4.club_name}/update_club_info/')

    

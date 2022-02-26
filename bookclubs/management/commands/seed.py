from django.core.management.base import BaseCommand, CommandError

from bookclubs.models import User, Club, Role, Book,Rating,ClubBookAverageRating

import pytz
from faker import Faker
from random import randint, random
from faker.providers import BaseProvider, address, date_time, misc
import pandas as pd
import datetime
import numpy
#from bookclubs.recommender.BooksRecommender import getGenra
import urllib.request
import json
import textwrap
class Command(BaseCommand):
    USER_COUNT = 100
    CLUB_COUNT = 10
    DEFAULT_PASSWORD = 'Password123'
    USER_IN_CLUB_PROBABILITY = 0.2
    USER_RATE_BOOK_PROBABILITY= 0.3
    #ratingsPath = 'bookclubs/recommender/dataset/BX-Book-Ratings.csv'
    booksPath   = 'bookclubs/recommender/dataset/BX-Books.csv'
    #usersPath   = 'bookclubs/recommender/dataset/BX-Users.csv'
    # df_ratings=[]
    # df_users=[]
    # df_books=[]
    


    def load_data_from_csv(self):
        #self.df_users= pd.read_csv(self.usersPath, sep = ';',names = ['User-ID', 'Location', 'Age'], quotechar = '"', encoding = 'latin-1',header = 0)
        self.df_books= pd.read_csv(self.booksPath, sep = ';',names = ['ISBN','Book-Title','Book-Author','Year-Of-Publication','Publisher','Image-URL-S','Image-URL-M','Image-URL-L'], quotechar = '"', encoding = 'latin-1',header = 0)
        #self.df_ratings= pd.read_csv(self.ratingsPath, sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0)


    def getGenra(self, isbn):
        base_api_link = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

        with urllib.request.urlopen(base_api_link + isbn) as f:
            text = f.read()

        decoded_text = text.decode("utf-8")
        obj = json.loads(decoded_text) # deserializes decoded_text to a Python object
        volume_info = obj["items"][0]

        return  volume_info["volumeInfo"]["categories"]

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.load_data_from_csv()
        self.create_books()
        self.books = Book.objects.all()

        self.create_users()
        # self.users = User.objects.all()
        # self.create_ratings()
        #
        # self._create_clubs()
        # self.clubs = Club.objects.all()
        # self._create_roles()
        # self.roles = Role.objects.all()
    # def create_ratings(self):
    #     for index, rating in self.df_ratings.iterrows():
    #         print(f"Seeding rating {index}/{len(self.df_ratings)}", end='\r')
    #
    #         try:
    #
    #             self.create_rating(rating)
    #         except:
    #             continue
    #     print("Rating seeding complete.      ")
    #
    # def create_rating(self,rating):
    #     Rating.objects.create(
    #         rate = rating['Book-Rating'],
    #         book = self.books.get(ISBN=rating['ISBN']),
    #         user = self.users.get(userID=rating['User-ID']  ))
    def create_ratings (self):
        for book in self.books:
            print(f"Seeding user ratings ......", end='\r')
            for user in self.users:
                try:
                    if random()<self.USER_RATE_BOOK_PROBABILITY:
                        self.create_rating(user, book)
                except:
                    continue
        print("Rating seeding complete.      ")

    def create_rating(self, user, book):
        rate = self.faker.random_int(min=0, max=10)
        Rating.objects.create(
            rate=rate,
            book=book,
            user=user
        )
    def create_books(self):
        for index, book in self.df_books.head(3).iterrows():
            print(f"Seeding book {index}/{len(self.df_books)}", end='\r')
            try:

                self.create_book(book)
            except:
                continue
        print("Book seeding complete.      ")

    def create_book(self,book):
        Book.objects.create(
            ISBN=book['ISBN'],
            title =book['Book-Title'],
            author = book['Book-Author'],
            year_of_publication =book['Year-Of-Publication'],
            publisher =book['Publisher'],
            image_url_s = book['Image-URL-S'],
            image_url_m =book['Image-URL-M'],
            image_url_l = book['Image-URL-L'],
            genra=self.getGenra(book['ISBN'])[0]
        )



    def create_users(self):
        user_count = 0
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            try:
                self.create_user(user_count)
            except:
                continue
            user_count += 1
        print("User seeding complete.      ")
    # def create_users(self):
    #     for index, user in self.df_users.iterrows():
    #         print(f"Seeding user {index}/{len(self.df_users)}", end='\r')
    #         try:
    #
    #             self.create_user(user)
    #         except:
    #             continue
    #     print("User seeding complete.      ")


    #the csv file has only user id, location and age so Other information are created with Faker
    # def create_user(self,user):
    #     first_name = self.faker.first_name()
    #     last_name = self.faker.last_name()
    #     email = create_email(first_name, last_name)
    #     username = create_username(first_name, last_name)
    #     bio = self.faker.text(max_nb_chars=520)
    #     #dob = self.faker.date_of_birth(minimum_age = 8, maximum_age = 100)
    #     dob=self.get_dob_from_age(user['Age'])
    #     gender = self.faker.random_choices(elements=('M', 'F', 'O'), length=1)[0]
    #     #location = self.faker.city()
    #     meeting_preference = self.faker.random_choices(elements=('O', 'P'), length=1)[0]
    #     User.objects.create_user(
    #         userID=user['User-ID'],
    #         username=username,
    #         email=email,
    #         password=Command.DEFAULT_PASSWORD,
    #         first_name=first_name,
    #         last_name=last_name,
    #         bio=bio,
    #         dob=dob,
    #         gender=gender,
    #         location=user['Location'],
    #         meeting_preference=meeting_preference
    #     )
    def create_user(self,userID):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        bio = self.faker.text(max_nb_chars=520)
        dob = self.faker.date_of_birth(minimum_age = 8, maximum_age = 100)
        #dob=self.get_dob_from_age(user['Age'])
        gender = self.faker.random_choices(elements=('M', 'F', 'O'), length=1)[0]
        location = self.faker.city()
        meeting_preference = self.faker.random_choices(elements=('O', 'P'), length=1)[0]
        User.objects.create_user(
            userID=userID+1,
            username=username,
            email=email,
            password=Command.DEFAULT_PASSWORD,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            dob=dob,
            gender=gender,
            location=location,
            meeting_preference=meeting_preference
        )

    # def get_dob_from_age(self, age):
    #     if numpy.isnan(age) :
    #         return None
    #     else:
    #         now = datetime.datetime.now()
    #         current_year = now.year
    #         year_of_birth=int(current_year-age)
    #         start_date = datetime.date(year=year_of_birth, month=1, day=1)
    #         end_date = datetime.date(year=year_of_birth, month=12, day=31)
    #         return self.faker.date_between(start_date=start_date, end_date=end_date)


    def _create_clubs(self):
        club_count = 0
        while club_count < self.CLUB_COUNT:
            print(f"Seeding club {club_count}/{self.CLUB_COUNT}", end='\r')
            try:
                club = self._create_club()
            except:
                continue
            club_count += 1
        print("Club seeding complete.      ")

    def _create_club(self):
        description = self.faker.text(max_nb_chars=520)
        meeting_status = self.faker.boolean()
        location = self.faker.street_name()
        club_name = create_club_name(location)
        public_status = self.faker.boolean()
        genre = self.faker.text(max_nb_chars=520)
        club = Club.objects.create(
            club_name=club_name,
            description=description,
            meeting_status=meeting_status,
            location=location,
            public_status=public_status,
            genre=genre
        )

    def _create_roles(self):
        role_count = 0
        for club in self.clubs:
            print(f"Seeding userInClub {role_count}/{self.CLUB_COUNT*self.USER_COUNT}", end='\r')
            self._create_owner_role(club)
            role_count += 1
            for user in self.users:
                try:
                    self._create_role(user, club)
                except:
                    continue
                role_count += 1
        print("Role seeding complete.      ")

    def _create_role(self, user, club):
        if random() < self.USER_IN_CLUB_PROBABILITY:
            club_role = self.faker.random_choices(elements=('MEM', 'OFF', 'MOD', 'BAN'), length=1)[0]
            Role.objects.create(
                user=user,
                club=club,
                club_role=club_role
            )

    def _create_owner_role(self, club):
        user = self.get_random_user()
        Role.objects.create(
            user=user,
            club=club,
            club_role='OWN'
        )

    def get_random_user(self):
        index = randint(0,self.users.count()-1)
        return self.users[index]

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

def create_club_name(location):
    return location + 'Book Club'

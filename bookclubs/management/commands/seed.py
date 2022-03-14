from django.core.management.base import BaseCommand, CommandError

from bookclubs.models import User, Club, Role, Book, ClubBookAverageRating
from bookclubs.models import User, Post, Comment, Club, Role, Book, BookRatingReview, Meeting

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
    POST_COUNT = 100
    COMMENT_COUNT = 100
    MEETING_COUNT = 10
    DEFAULT_PASSWORD = 'Password123'
    USER_IN_CLUB_PROBABILITY = 0.2
    USER_RATE_BOOK_PROBABILITY= 0.3
    #ratingsPath = 'bookclubs/recommender/dataset/BX-Book-Ratings.csv'
    booksPath   = 'bookclubs/dataset/BX-Books.csv'
    #usersPath   = 'bookclubs/recommender/dataset/BX-Users.csv'
    # df_ratings=[]
    # df_users=[]
    # df_books=[]
    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.load_data_from_csv()

        self.create_books()
        self.books = Book.objects.all()

        self.create_users()
        self.users = User.objects.all()

        self.create_ratings()

        self.create_posts()
        self.posts = Post.objects.all()

        self.create_comments()

        self.create_clubs()
        self.clubs = Club.objects.all()

        self.create_roles()

        # self.create_meetings()



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

    # def __init__(self):
    #     self.faker = Faker('en_GB')
    #
    # def handle(self, *args, **options):
    #     self.load_data_from_csv()
    #     self.create_books()
    #     self.books = Book.objects.all()
    #
    #     self.create_users()
    #     self.users = User.objects.all()
    #     self.create_ratings()
    #
    #     self.create_clubs()
    #     self.clubs = Club.objects.all()
    #     self.create_roles()
    #     self.roles = Role.objects.all()
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
        BookRatingReview.objects.create(
            rate=rate,
            book=book,
            user=user
        )
    def create_books(self):
        for index, book in self.df_books.head(100).iterrows():
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

    def create_user(self, userID):
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


    def create_clubs(self):
        club_count = 0
        while club_count < self.CLUB_COUNT:
            print(f"Seeding club {club_count}/{self.CLUB_COUNT}", end='\r')
            try:
                club = self.create_club()
            except:
                continue
            club_count += 1
        print("Club seeding complete.      ")

    def create_club(self):
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

    def create_roles(self):
        role_count = 0
        for club in self.clubs:
            # print(f"Seeding role {role_count}/{self.CLUB_COUNT*len(self.df_users)}", end='\r')
            print(f"Seeding role {role_count}/{self.CLUB_COUNT*10}", end='\r')
            self.create_owner_role(club)
            role_count += 1
            for user in self.users:
                try:
                    self.create_role(user, club)
                except:
                    continue
                role_count += 1
        print("Role seeding complete.      ")

    def create_role(self, user, club):
        if random() < self.USER_IN_CLUB_PROBABILITY:
            club_role = self.faker.random_choices(elements=('MEM', 'MOD', 'BAN'), length=1)[0]
            Role.objects.create(
                user=user,
                club=club,
                club_role=club_role
            )

    def create_owner_role(self, club):
        user = self.get_random_user()
        Role.objects.create(
            user=user,
            club=club,
            club_role='OWN'
        )

    def get_random_user(self):
        index = randint(0,self.users.count()-1)
        return self.users[index]

    def create_posts(self):
        for i in range(self.POST_COUNT):
            print(f"Seeding post {i}/{self.POST_COUNT}", end='\r')
            self.create_post()
        print("Post seeding complete.      ")

    def create_post(self):
        post = Post()
        post.title = self.faker.text(max_nb_chars=255)
        post.author = self.get_random_user()
        post.body = self.faker.text(max_nb_chars=280)
        post.save()
        datetime = self.faker.past_datetime(start_date='-365d', tzinfo=pytz.UTC)
        Post.objects.filter(id=post.id).update(post_datetime = datetime)

    def create_comments(self):
        for i in range(self.COMMENT_COUNT):
            print(f"Seeding comment {i}/{self.COMMENT_COUNT}", end='\r')
            self.create_comment()
        print("Comment seeding complete.      ")

    def create_comment(self):
        comment = Comment()
        comment.author = self.get_random_user()
        comment.body = self.faker.text(max_nb_chars=280)
        comment.related_post = self.get_random_post()
        comment.save()
        datetime = self.faker.past_datetime(start_date='-365d', tzinfo=pytz.UTC)
        Comment.objects.filter(id=comment.id).update(created_at = datetime)

    def get_random_post(self):
        index = randint(0,self.posts.count()-1)
        return self.posts[index]

    def create_meetings(self):
        meeting_count = 0
        while meeting_count < self.MEETING_COUNT:
            print(f"Seeding meeting {meeting_count}/{self.MEETING_COUNT}", end='\r')
            try:
                meeting = self.create_meeting()
            except:
                continue
            meeting_count += 1
        print("Club seeding complete.      ")

    def create_meeting(self):
        club = self.get_random_club()
        topic = self.faker.text(max_nb_chars=120)
        description = self.faker.text(max_nb_chars=520)
        meeting_status = self.faker.boolean()
        location = self.faker.street_name()
        date = self.faker.past_datetime(start_date='-365d', tzinfo=pytz.UTC)
        time_start = self.faker.time()
        time_end = self.faker.time()
        meeting = Meeting.objects.create(
            club=club,
            topic=topic,
            description=description,
            meeting_status=meeting_status,
            location=location,
            date=date,
            time_start=time_start,
            time_end=time_end
        )

    def get_random_club(self):
        index = randint(0,self.clubs.count()-1)
        return self.clubs[index]

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

def create_club_name(location):
    return location + ' Book Club'

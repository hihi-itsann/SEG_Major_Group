from ntpath import join
from django.core.management.base import BaseCommand, CommandError
from bookclubs.meeting_link import create_zoom_meeting, get_join_link, get_start_link

from bookclubs.models import User, Post, Vote, Comment, Club, Role, Book, BookRatingReview, Meeting, MeetingAttendance, \
    Application, ClubBookAverageRating

import pytz
from faker import Faker
from random import randint, random, choice
from faker.providers import BaseProvider, address, date_time, misc
import pandas as pd
import datetime
import numpy
# from bookclubs.recommender.BooksRecommender import getgenre
import urllib.request
import json
import textwrap


class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    USER_COUNT = 100
    CLUB_COUNT = 10
    POST_COUNT = 100
    COMMENT_COUNT = 100
    MEETING_PER_CLUB_COUNT = 2
    APPLICATION_PER_CLUB_COUNT = 10
    MEETING_ATTENDANCE_PER_MEETING = 5
    DEFAULT_PASSWORD = 'Password123'
    USER_IN_CLUB_PROBABILITY = 0.2
    USER_RATE_BOOK_PROBABILITY = 0.3
    USER_VOTE_POST_PROBABILITY = 0.7
    # ratingsPath = 'bookclubs/recommender/dataset/BX-Book-Ratings.csv'
    booksPath = 'bookclubs/dataset/BX-Books.csv'

    # usersPath   = 'bookclubs/recommender/dataset/BX-Users.csv'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):

        self.load_data_from_csv()

        self.create_books()
        self.books = Book.objects.all()

        self.create_users()
        self.users = User.objects.all()

        self.create_ratings()

        self.create_clubs()
        self.clubs = Club.objects.all()

        self.create_roles()

        self.create_applications()

        self.create_posts()
        self.posts = Post.objects.all()

        self.create_comments()

        self.create_votes()

        self.create_meetings()
        self.meetings = Meeting.objects.all()

        self.create_meeting_attendance()

    def load_data_from_csv(self):
        # self.df_users= pd.read_csv(self.usersPath, sep = ';',names = ['User-ID', 'Location', 'Age'], quotechar = '"', encoding = 'latin-1',header = 0)
        self.df_books = pd.read_csv(self.booksPath, sep=';',
                                    names=['ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher',
                                           'Image-URL-S', 'Image-URL-M', 'Image-URL-L'], quotechar='"',
                                    encoding='latin-1', header=0)
        # self.df_ratings= pd.read_csv(self.ratingsPath, sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0)

    def getgenre(self, isbn):
        base_api_link = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

        with urllib.request.urlopen(base_api_link + isbn) as f:
            text = f.read()

        decoded_text = text.decode("utf-8")
        obj = json.loads(decoded_text)  # deserializes decoded_text to a Python object
        volume_info = obj["items"][0]

        return volume_info["volumeInfo"]["categories"]

    def create_ratings(self):
        for book in self.books:
            print(f"Seeding user ratings ......", end='\r')
            for user in self.users:
                try:
                    if random() < self.USER_RATE_BOOK_PROBABILITY:
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
            # print(f"Seeding book {index}/{len(self.df_books)}", end='\r')
            print(f"Seeding book {index}/100", end='\r')
            try:

                self.create_book(book)
            except:
                continue
        print("Book seeding complete.      ")

    def create_book(self, book):
        Book.objects.create(
            ISBN=book['ISBN'],
            title=book['Book-Title'],
            author=book['Book-Author'],
            year_of_publication=book['Year-Of-Publication'],
            publisher=book['Publisher'],
            image_url_s=book['Image-URL-S'],
            image_url_m=book['Image-URL-M'],
            image_url_l=book['Image-URL-L'],
            genre=(self.getgenre(book['ISBN'])[0]).lower().title()
        )

    def create_users(self):
        user_count = 0
        print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
        try:
            self.create_gravatar_user()
            user_count = 1
        except:
            pass
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            try:
                self.create_user(user_count)
            except:
                continue
            user_count += 1
        print("User seeding complete.      ")

    def create_user(self, user_count):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        bio = self.faker.text(max_nb_chars=520)
        dob = self.faker.date_of_birth(minimum_age=8, maximum_age=100)
        # dob=self.get_dob_from_age(user['Age'])
        gender = self.faker.random_choices(elements=('M', 'F', 'O'), length=1)[0]
        location = self.faker.street_name()
        city = self.faker.city()
        country = self.faker.country()
        meeting_preference = self.faker.random_choices(elements=('O', 'P'), length=1)[0]
        User.objects.create_user(
            userID=user_count + 1,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.DEFAULT_PASSWORD,

            bio=bio,
            dob=dob,
            gender=gender,
            location=location,
            city=city,
            country=country,
            meeting_preference=meeting_preference
        )

    def create_gravatar_user(self):
        # Should always be userID = 0 as it is the first seeded user
        if User.objects.filter(email__exact="getgoogle@hotmail.com"):
            pass
        else:
            first_name = self.faker.first_name()
            last_name = 'Gravatar'
            email = 'getgoogle@hotmail.com'
            # This is not a fake email, but it is an inactive email that has been set up for this purpose and has a
            # gravatar account associated with it
            username = '@gravatar'
            bio = self.faker.text(max_nb_chars=520)
            dob = self.faker.date_of_birth(minimum_age=8, maximum_age=100)
            gender = self.faker.random_choices(elements=('M', 'F', 'O'), length=1)[0]
            location = self.faker.street_name()
            city = self.faker.city()
            country = self.faker.country()
            meeting_preference = self.faker.random_choices(elements=('O', 'P'), length=1)[0]
            gravatar_user = User.objects.create_user(
                userID=0,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=Command.DEFAULT_PASSWORD,
                bio=bio,
                dob=dob,
                gender=gender,
                location=location,
                city=city,
                country=country,
                meeting_preference=meeting_preference
            )

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
        meeting_status = self.faker.random_choices(elements=('ONL', 'OFF'), length=3)[0]
        location = self.faker.street_name()
        city = self.faker.city()
        country = self.faker.country()
        club_name = create_club_name(location)
        public_status = self.faker.random_choices(elements=('PUB', 'PRI'), length=3)[0]
        genre = self.faker.text(max_nb_chars=520)
        club = Club.objects.create(
            club_name=club_name,
            description=description,
            meeting_status=meeting_status,
            location=location,
            city=city,
            country=country,
            public_status=public_status,
            genre=genre
        )

    def create_roles(self):

        self.create_owner_role()
        for i in range(self.USER_COUNT - self.CLUB_COUNT):
            print(f"Seeding other role {i}/{self.USER_COUNT - self.CLUB_COUNT}", end='\r')
            try:
                self.create_role(self.users[i + self.CLUB_COUNT + 1], self.get_random_club())
            except:
                continue
        print("Role seeding complete.      ")

    def create_role(self, user, club):
        club_role = self.faker.random_choices(elements=('MEM', 'MOD', 'BAN'), length=1)[0]
        Role.objects.create(
            user=user,
            club=club,
            club_role=club_role
        )

    def create_owner_role(self):
        for i in range(self.CLUB_COUNT):
            print(f"Seeding owner role {i + 1}/{self.CLUB_COUNT}", end='\r')
            Role.objects.create(
                user=self.users[i],
                club=self.clubs[i],
                club_role='OWN'
            )
        print("Owner role seeding complete.      ")

    def get_random_user(self):
        index = randint(0, self.users.count() - 1)
        return self.users[index]

    def create_posts(self):
        for i in range(self.POST_COUNT):
            print(f"Seeding post {i}/{self.POST_COUNT}", end='\r')
            self.create_post()
        print("Post seeding complete.      ")

    def create_post(self):
        post = Post()
        post.title = self.faker.text(max_nb_chars=255)
        post.club = self.get_random_club()
        post.author = self.get_random_member(post.club)
        post.body = self.faker.text(max_nb_chars=280)
        post.save()
        datetime = self.faker.past_datetime(start_date='-365d', tzinfo=pytz.UTC)
        Post.objects.filter(id=post.id).update(post_datetime=datetime)

    def create_comments(self):
        for i in range(self.COMMENT_COUNT):
            print(f"Seeding comment {i}/{self.COMMENT_COUNT}", end='\r')
            self.create_comment()
        print("Comment seeding complete.      ")

    def create_comment(self):
        club = self.get_random_club()
        comment = Comment()
        comment.author = self.get_random_member(club)
        comment.body = self.faker.text(max_nb_chars=280)
        comment.related_post = self.get_random_post(club)
        comment.save()
        datetime = self.faker.past_datetime(start_date='-365d', tzinfo=pytz.UTC)
        Comment.objects.filter(id=comment.id).update(created_at=datetime)

    # get random post from a specific club
    def get_random_post(self, club):
        club_post = Post.objects.all().filter(club=club)
        index = randint(0, club_post.count() - 1)
        return club_post[index]

    def create_meetings(self):
        meeting_count = 0
        for club in self.clubs:
            for meet in range(0, self.MEETING_PER_CLUB_COUNT):
                print(f"Seeding meeting {meeting_count}/{self.MEETING_PER_CLUB_COUNT * self.CLUB_COUNT}", end='\r')
                try:
                    self.create_meeting()
                except:
                    continue
                meeting_count += 1
        print("Meeting seeding complete.      ")

    def create_meeting(self):
        date = self.faker.future_date()
        time_start = self.faker.time(pattern='%H:%M')
        duration = randint(15, 45)
        club = self.get_random_club()
        book = self.get_random_book()
        topic = self.faker.text(max_nb_chars=60)
        description = self.faker.text(max_nb_chars=520)
        meeting_status = club.meeting_status
        if meeting_status == 'ONL':
            location = 'Meeting link to be created...'
            create_zoom_meeting(date, time_start, duration)
            join_link = get_join_link()
            start_link = get_start_link()

        else:
            location = self.faker.street_name()
            join_link = None
            start_link = None
        meeting = Meeting.objects.create(
            club=club,
            book=book,
            topic=topic,
            description=description,
            meeting_status=meeting_status,
            location=location,
            date=date,
            time_start=time_start,
            duration=duration,
            join_link=join_link,
            start_link=start_link
        )

    def get_random_club(self):
        index = randint(0, self.clubs.count() - 1)
        return self.clubs[index]

    def get_random_book(self):
        index = randint(0, self.books.count() - 1)
        return self.books[index]

    def create_meeting_attendance(self):
        meeting_attendance_count = 0
        for meeting in self.meetings:
            meeting_attendance_count += 1
            host = self.create_meeting_host(meeting)
            for i in range(self.MEETING_ATTENDANCE_PER_MEETING - 1):
                print(
                    f"Seeding attendance {meeting_attendance_count}/{self.MEETING_PER_CLUB_COUNT * self.CLUB_COUNT * self.MEETING_ATTENDANCE_PER_MEETING}",
                    end='\r')
                try:
                    self.create_meeting_attendee(meeting, host)
                except:
                    continue
                meeting_attendance_count += 1
        print("Meeting Attendance seeding complete.      ")

    def create_meeting_host(self, meeting):
        meeting_host = MeetingAttendance.objects.create(
            user=self.get_random_member(meeting.club),
            meeting=meeting,
            meeting_role='H'
        )
        return meeting_host

    def create_meeting_attendee(self, meeting, host):
        random_member = self.get_random_member(meeting.club)
        if random_member != host:
            MeetingAttendance.objects.create(
                user=random_member,
                meeting=meeting,
                meeting_role='A'
            )

    def get_random_member(self, club):
        member_roles = Role.objects.all().filter(club=club).exclude(club_role='BAN')
        index = randint(0, member_roles.count() - 1)
        return member_roles[index].user

    def create_applications(self):
        application_count = 0
        for club in self.clubs:
            priv_club_count = self.clubs.filter(public_status='PRI').count()
            if club.public_status == 'PRI':
                for i in range(0, self.APPLICATION_PER_CLUB_COUNT):
                    print(f"Seeding application {application_count}/{self.APPLICATION_PER_CLUB_COUNT * priv_club_count}"
                          , end='\r')
                    try:
                        self.create_application(club)
                    except:
                        continue
                    application_count += 1
        print("Application seeding complete.      ")

    def create_application(self, club):
        user = self.get_random_non_member(club)
        statement = self.faker.text(max_nb_chars=200)
        Application.objects.create(
            user=user,
            club=club,
            statement=statement,
            status='P'
        )

    def get_random_non_member(self, club):
        all_in_club = Role.objects.filter(club=club).values_list('user', flat=True)
        all_out_of_club = User.objects.all().exclude(id__in=all_in_club)
        index = randint(0, all_out_of_club.count() - 1)
        return all_out_of_club[index]

    def create_votes(self):
        self.users
        for post in self.posts:
            print(f"Seeding votes...", end='\r')
            user_ids = Role.objects.filter(club=post.club).exclude(club_role='BAN').values_list('user', flat=True)
            users_in_club = self.users.filter(id__in=user_ids)
            for user in users_in_club:
                try:
                    if random() < self.USER_VOTE_POST_PROBABILITY:
                        self.create_vote(user, post)
                except:
                    continue
        print("Vote seeding complete.      ")

    def create_vote(self, user, post):
        vote_type = bool(choice([True, False]))
        Vote.objects.create(
            user=user,
            post=post,
            vote_type=vote_type
        )


def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()


def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'


def create_club_name(location):
    return location + ' Book Club'

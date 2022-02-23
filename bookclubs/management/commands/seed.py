from django.core.management.base import BaseCommand, CommandError

from bookclubs.models import User, Post, Comment, Club, Role

import pytz
from faker import Faker
from random import randint, random
from faker.providers import BaseProvider, address, date_time, misc


class Command(BaseCommand):
    USER_COUNT = 100
    POST_COUNT = 2000
    CLUB_COUNT = 10
    COMMENT_COUNT = 2000
    DEFAULT_PASSWORD = 'Password123'
    USER_IN_CLUB_PROBABILITY = 0.2

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_posts()
        self.posts = Post.objects.all()
        # self.create_comments()
        self.create_clubs()
        self.clubs = Club.objects.all()
        self.create_roles()

    def create_users(self):
        user_count = 0
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            try:
                self.create_user()
            except:
                continue
            user_count += 1
        print("User seeding complete.      ")

    def create_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        bio = self.faker.text(max_nb_chars=520)
        dob = self.faker.date_of_birth(minimum_age = 8, maximum_age = 100)
        gender = self.faker.random_choices(elements=('M', 'F', 'O'), length=1)[0]
        location = self.faker.city()
        meeting_preference = self.faker.random_choices(elements=('O', 'P'), length=1)[0]
        User.objects.create_user(
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
            print(f"Seeding userInClub {role_count}/{self.CLUB_COUNT*self.USER_COUNT}", end='\r')
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

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

def create_club_name(location):
    return location + 'Book Club'

from django.core.management.base import BaseCommand, CommandError

from bookclubs.models import User
from bookclubs.models import Post

import pytz
from faker import Faker
from random import randint, random
from faker.providers import BaseProvider, address, date_time


class Command(BaseCommand):
    USER_COUNT = 100
    DEFAULT_PASSWORD = 'Password123'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()

    def create_users(self):
        user_count = 1
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

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

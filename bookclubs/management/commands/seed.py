from django.core.management.base import BaseCommand, CommandError

from bookclubs.models import User, Club, Role

import pytz
from faker import Faker
from random import randint, random
from faker.providers import BaseProvider, address, date_time, misc


class Command(BaseCommand):
    USER_COUNT = 100
    CLUB_COUNT = 10
    DEFAULT_PASSWORD = 'Password123'
    USER_IN_CLUB_PROBABILITY = 0.2

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self._create_clubs()
        self.clubs = Club.objects.all()
        self._create_roles()
        self.roles = Role.objects.all()

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

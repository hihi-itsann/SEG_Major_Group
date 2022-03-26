import datetime
import traceback
from django.contrib import messages
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar
from django.db.models import Avg
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import json

class User(AbstractUser):
    userID = models.IntegerField(unique=True, null=True)
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumerics'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    dob = models.DateField(blank=True,
                           null=True)  # blank=False, auto_now_add=False, auto_now=False, default=date.today())
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    location = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    # country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    # city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)

    MEETING_CHOICES = (
        ('O', 'Online'),
        ('P', 'In-person')
    )
    meeting_preference = models.CharField(max_length=1, choices=MEETING_CHOICES, blank=True)

    
    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    def get_pronouns(self):
        if self.gender == 'M':
            return f'he/ him'
        elif self.gender == 'F':
            return f'she/ her'
        else:
            return f'they/ them (consult for other pronouns)'

    def get_clubs(self):
        users_clubs = Role.objects.filter(user=self).exclude(club_role='BAN').values_list('club', flat=True)
        return Club.objects.filter(id__in=users_clubs)

    def get_applied_clubs(self):
        applicant_clubs = Application.objects.filter(user=self, status='P').values_list('club', flat=True)
        return Club.objects.filter(id__in=applicant_clubs)



class Book(models.Model):
    ISBN = models.CharField(
        primary_key=True,
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(10)]  # ISBN has fixed length 10
    )
    title = models.CharField(max_length=100, unique=True, blank=False)
    author = models.CharField(max_length=100, blank=False)
    year_of_publication = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(2022)],
                                              blank=False)
    publisher = models.CharField(max_length=100, blank=False)
    image_url_s = models.URLField(blank=False)
    image_url_m = models.URLField(blank=False)
    image_url_l = models.URLField(blank=False)
    genre = models.CharField(max_length=100, blank=True)

    def getAverageRate(self):
        return self.bookratingreview_set.all().aggregate(Avg('rate'))['rate__avg']

    def getReview(self):
        return BookRatingReview.objects.filter(book=self).exclude(review__exact='')

    def get_ISBN(self):
        return self.ISBN
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    @staticmethod
    def get_genres():
        genres = [('Fiction', 'Fiction'), ('Non-Fiction', 'Non-Fiction')]
        try:
            books = Book.objects.all()
            if books.count() > 0:
                for book in books:
                    genres.append((book.genre.title(), book.genre.title()))
                genres = list(set(genres))
        except:
            # print(traceback.format_exc())
            print("Genres are being set to the default of Fiction and Non-Fiction until books are added to the system.")
        finally:
            return genres

    # def getReadingStatus(self,user):
    #     return BookStatus.objects.get(user=user, book=self).status
    class Meta:
        ordering = ['title']
        # return self.rating_set.all().aggregate(Avg('rate'))['rate__avg']


class BookRatingReview(models.Model):
    rate = models.FloatField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.CharField(max_length=520, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class BookStatus(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('U', 'Unread'),
        ('R', 'Reading'),
        ('F', 'Finished')
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=False, default='U')

    def change_status(self, choice):
        if choice == 'U':
            self.status = 'U'
            self.save()
        elif choice == 'R':
            self.status = 'R'
            self.save()
        elif choice == 'F':
            self.status = 'F'
            self.save()
        else:
            pass


class Application(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('R', 'Rejected')
    )
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    statement = models.CharField(max_length=520, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'club')

    def change_status(self, choice):
        if choice == 'A':
            self.status = 'A'
        elif choice == 'R':
            self.status = 'R'
        else:
            self.status = 'P'
        self.save()


class Club(models.Model):
    MEETING_CHOICES = (
        ('ONL', 'Online'),
        ('OFF', 'In-person')
    )
    PRIVACY_CHOICES = (
        ('PUB', 'Public'),
        ('PRI', 'Private')
    )

    club_name = models.CharField(
        unique=True,
        max_length=20,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^\w{4,}.*$',
                message='Club name must consist of at least four alphanumerics in first word'
            )
        ]
    )

    meeting_status = models.CharField(
        choices=MEETING_CHOICES,
        default='OFF',
        max_length=3
    )

    location = models.CharField(
        max_length=100,
        blank=False
    )
    city = models.CharField(
        max_length=100,
        blank=True
    )
    country = models.CharField(
        max_length=100,
        blank=True
    )
    # country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    # city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)

    public_status = models.CharField(
        choices=PRIVACY_CHOICES,
        default='PRI',
        max_length=3
    )

    genre = models.CharField(
        max_length=100,
        default='Fiction',
        blank=False
    )

    description = models.CharField(
        max_length=520,
        blank=False
    )

    club_members = models.ManyToManyField(User, through='Role')

    def get_club_name(self):
        """Return club name"""
        return self.club_name

    def get_club_role(self, user):
        """Return the club role for the user (already part of the club)"""
        return Role.objects.get(club=self, user=user).club_role

    def toggle_member(self, user):
        """User that is part of the club becomes a member"""
        role = Role.objects.get(club=self, user=user)
        if role.club_role == 'OWN' or role.club_role == 'BAN':
            return
        else:
            role.club_role = 'MEM'
            role.save()

    def toggle_moderator(self, user):
        """User that is part of the club becomes a moderator"""
        role = Role.objects.get(club=self, user=user)
        if role.club_role == 'OWN' or role.club_role == 'BAN':
            return
        else:
            role.club_role = 'MOD'
            role.save()
            return

    def ban_member(self, user):
        """User is banned from the club, they cannot re-apply to join"""
        role = Role.objects.get(club=self, user=user)
        if role.club_role == 'OWN' or role.club_role == 'BAN':
            return
        else:
            role.club_role = 'BAN'
            role.save()
            return

    def unban_member(self, user):
        """Unban a banned user, they can now re-apply to join the club."""
        role = Role.objects.get(club=self, user=user)
        if role.club_role == 'BAN':
            role.club_role = 'MEM'
            role.save()
            return
        else:
            return

    def transfer_ownership(self, old_owner, new_owner):
        """Transfer ownership to a moderator in the club"""
        new_owner_role = Role.objects.get(club=self, user=new_owner)
        old_owner_role = Role.objects.get(club=self, user=old_owner)
        if old_owner_role.club_role == 'OWN' and new_owner_role.club_role == 'MOD':
            new_owner_role.club_role = 'OWN'
            new_owner_role.save()
            old_owner_role.club_role = 'MOD'
            old_owner_role.save()
            return

        else:
            return

    def remove_user_from_club(self, user):
        """User is removed from the club, however they can re-apply to join the club immediately after"""
        role = Role.objects.get(club=self, user=user)
        if role.club_role == 'OWN' or role.club_role == 'BAN':
            return
        else:
            role.delete()
            if Application.objects.filter(user=user, club=self).count() == 1:
                Application.objects.get(user=user, club=self).delete()

    def get_members(self):
        return self.club_members.all().filter(
            club__club_name=self.club_name, role__club_role='MEM')

    def get_moderators(self):
        return self.club_members.all().filter(
            club__club_name=self.club_name, role__club_role='MOD')

    def get_management(self):
        return self.club_members.all().filter(
            club__club_name=self.club_name, role__club_role='MOD') | self.club_members.all().filter(
            club__club_name=self.club_name, role__club_role='OWN')

    def get_banned_members(self):
        return self.club_members.all().filter(
            club__club_name=self.club_name,
            role__club_role='BAN')

    def get_owner(self):
        return User.objects.all().filter(
            club__club_name=self.club_name,
            role__club_role='OWN')

    def get_meeting_status(self):
        if self.meeting_status == 'ONL':
            return 'Online'
        else:
            return 'In-Person'

    def get_public_status(self):
        if self.public_status == 'PRI':
            return 'Private'
        else:
            return 'Public'


class Role(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    class RoleOptions(models.TextChoices):
        MEMBER = 'MEM', _('Member')
        MODERATOR = 'MOD', _('Moderator')
        OWNER = 'OWN', _('Owner')
        BANNED = 'BAN', _('Banned')

    club_role = models.CharField(
        max_length=3,
        choices=RoleOptions.choices,
        default=RoleOptions.MEMBER,
        # unique=True,
    )

    class Meta:
        unique_together = ('user', 'club')

    def get_club_role(self):
        return self.RoleOptions(self.club_role).name.title()


class Post(models.Model):

    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    body = models.CharField(max_length=520, blank=False)
    post_date = models.DateField(auto_now_add=True)
    post_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-post_date', '-post_datetime']

    def __str__(self):
        return self.title + ' | ' + str(self.author)

    def toggle_upvote(self, user):
        if Vote.objects.filter(post=self, user=user).count() == 1:
            vote = Vote.objects.get(post=self, user=user)
            if vote.vote_type == True:
                vote.delete()
            else:
                vote.delete()
                Vote.objects.create(post=self, user=user, vote_type=True)
        else:
            Vote.objects.create(post=self, user=user, vote_type=True)

    def toggle_downvote(self, user):
        if Vote.objects.filter(post=self, user=user).count() == 1:
            vote = Vote.objects.get(post=self, user=user)
            if vote.vote_type == False:
                vote.delete()
            else:
                vote.delete()
                Vote.objects.create(post=self, user=user, vote_type=False)

        else:
            Vote.objects.create(post=self, user=user, vote_type=False)

    def get_upvotes(self):
        return Vote.objects.filter(post=self, vote_type=True).count()

    def get_downvotes(self):
        return Vote.objects.filter(post=self, vote_type=False).count()




class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_vote')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_vote')
    vote_type = models.BooleanField()

    class Meta:
        unique_together = ('user', 'post')


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=520, blank=False)
    related_post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Meeting(models.Model):
    MEETING_CHOICES = (
        ('ONL', 'Online'),
        ('OFF', 'In-person')
    )

    club = models.ForeignKey(Club, related_name='meeting_club', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True, )
    topic = models.CharField(max_length=120, default='', blank=False)
    description = models.TextField(max_length=520, blank=True)
    meeting_status = models.CharField(choices=MEETING_CHOICES, default='OFF', max_length=3)
    location = models.CharField(max_length=120, blank=True)
    date = models.DateField(blank=False)
    time_start = models.TimeField(blank=False)
    duration = models.IntegerField(blank=False, default=30)
    join_link = models.URLField(blank=True, null=True)
    start_link = models.URLField(blank=True,null=True)
    def get_time_end(self):
        time1 = self.time_start
        timedelta = datetime.timedelta(minutes=self.duration)
        tmp_datetime = datetime.datetime.combine(self.date, time1)
        time2 = (tmp_datetime + timedelta).time()
        return time2

    def is_attending(self, user):
        return (MeetingAttendance.objects.filter(meeting=self, user=user)).count() == 1

    def is_host(self, user):
        return (MeetingAttendance.objects.filter(meeting=self, user=user, meeting_role='H')).count() == 1

    def is_attendee_only(self, user):
        return (MeetingAttendance.objects.filter(meeting=self, user=user, meeting_role='A')).count() == 1

    def get_host(self):
        return MeetingAttendance.objects.get(meeting=self, meeting_role='H').user

    def get_meeting_status(self):
        if self.meeting_status == 'ONL':
            return 'Online'
        else:
            return 'In-Person'

    def get_is_time(self):
        return datetime.datetime.now().date()==self.date and datetime.datetime.now().time() > self.time_start and datetime.datetime.now().time() < self.get_time_end()

    def get_location(self):
        if self.meeting_status == 'ONL':
            if not self.get_is_time():
                return f"Meeting Link will be available when it's time"
            else:
                return f"It's time to join the meeting!"


        else:
            return f'Meeting Held: {self.location} {self.club.city} {self.club.country}'

    class Meta:
        ordering = ['-date']


class MeetingAttendance(models.Model):
    MEETING_ROLE_CHOICES = (
        ('H', 'Host'),
        ('A', 'Attendee')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    meeting_role = models.CharField(max_length=1, choices=MEETING_ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'meeting')


class ClubBookAverageRating(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rate = models.FloatField(default=0)
    number_of_ratings = models.IntegerField()

    def add_rating(self, rate):
        self.rate += rate
        self.save()

    def increment_number_of_ratings(self):
        self.number_of_ratings += 1
        self.save()

from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import When
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar
from datetime import date
from django.urls import reverse
from datetime import datetime, date
from django.utils.translation import gettext_lazy as _
from enum import Enum
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumbericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    dob = models.DateField(blank=True,null=True)#blank=False, auto_now_add=False, auto_now=False, default=date.today())
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    location = models.CharField(max_length=50, blank=True)
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


class Application(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    statement = models.CharField(max_length=520, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, blank=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'club')


class Club(models.Model):
    MEETING_STATUS_CHOICES = (
        (True, 'Online'),
        (False, 'In Person')
    )
    PUBLIC_STATUS_CHOICES = (
        (True, 'Public'),
        (False, 'Private')
    )

    club_name = models.CharField(
        unique=True,
        max_length=20,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^\w{4,}.*$',
                message='Club name must consist of at least four alphanumericals in first word'
            )
        ]
    )

    meeting_status = models.BooleanField(
        choices=MEETING_STATUS_CHOICES,
        default=False
    )

    location = models.CharField(
        max_length=100,
        blank=False
    )

    public_status = models.BooleanField(
        choices=PUBLIC_STATUS_CHOICES,
        default=True
    )

    genre = models.CharField(
        max_length=520,
        default='',
        blank=False
    )

    description = models.CharField(
        max_length=520,
        blank=False)

    club_members = models.ManyToManyField(User, through='Role')

    def get_club_role(self, user):
        return Role.objects.get(club=self, user=user).club_role

    def toggle_member(self, user):
        role = Role.objects.get(club=self, user=user)
        role.club_role = 'MEM'
        role.save()

    def toggle_officer(self, user):
        role = Role.objects.get(club=self, user=user)
        if role.club_role == 'APP' or role.club_role == 'BAN':
            return
        else:
            role.club_role = 'OFF'
            role.save()
            return

    def toggle_moderator(self, user):
        role = Role.objects.get(club=self, user=user)
        if role.club_role == 'APP' or role.club_role == 'BAN':
            return
        else:
            role.club_role = 'MOD'
            role.save()
            return

    def ban_member(self, user):
        role = Role.objects.get(club=self, user=user)
        if role.club_role == 'MEM':
            role.club_role = 'BAN'
            role.save()
            return
        else:
            return

    def unban_member(self, user):
        role = Role.objects.get(club=self, user=user)
        if role.club_role == 'BAN':
            role.delete()
            return
        else:
            return

    def transfer_ownership(self, old_owner, new_owner):
        new_owner_role = Role.objects.get(club=self, user=new_owner)
        old_owner_role = Role.objects.get(club=self, user=old_owner)
        if new_owner_role.club_role == 'OFF':
            new_owner_role.club_role = 'OWN'
            new_owner_role.save()
            old_owner_role.club_role = 'OFF'
            old_owner_role.save()
            return
        else:
            return

    def get_applicants(self):
        return self.club_members.all().filter(
            club__club_name=self.club_name,
            role__club_role='APP')

    def get_members(self):
        return self.club_members.all().filter(
            club__club_name=self.club_name, role__club_role='MEM')

    def get_management(self):
        return self.club_members.all().filter(
            club__club_name=self.club_name, role__club_role='OFF') | self.club_members.all().filter(
            club__club_name=self.club_name, role__club_role='OWN')

    def get_banned_members(self):
        return self.club_members.all().filter(
            club__club_name=self.club_name,
            role__club_role='BAN')

    def get_officers(self):
        return User.objects.all().filter(
            club__club_name=self.club_name,
            role__club_role='OFF')

    def get_owner(self):
        return User.objects.all().filter(
            club__club_name=self.club_name,
            role__club_role='OWN')

    def remove_user_from_club(self, user):
        role = Role.objects.get(club=self, user=user)
        role.delete()


class Role(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    class RoleOptions(models.TextChoices):
        APPLICANT = 'APP', _('Applicant')
        MEMBER = 'MEM', _('Member')
        OFFICER = 'OFF', _('Officer')
        MODERATOR = 'MOD', _('Moderator')
        OWNER = 'OWN', _('Owner')
        BANNED = 'BAN', _('BannedMember')

    club_role = models.CharField(
        max_length=3,
        choices=RoleOptions.choices,
        default=RoleOptions.APPLICANT,
    )

    def get_club_role(self):
        return self.RoleOptions(self.club_role).name.title()

class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    post_date = models.DateField(auto_now_add=True)
    post_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title + ' | ' + str(self.author)

    def get_absolute_url(self):
        return reverse('feed')

from django.core.validators import RegexValidator, MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar

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
    #dob = models.DateField(blank=False)

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

class Book(models.Model):
    ISBN = models.CharField(
        primary_key=True,
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(10)] #ISBN has fiexed length 10
    )
    title = models.CharField(max_length=100, unique=True, blank=False)
    author = models.CharField(max_length=100, blank=False)
    year_of_publication = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(2022)], blank=False)
    publisher = models.CharField(max_length=100, blank=False)
    image_url_s = models.URLField(blank=False)
    image_url_m = models.URLField(blank=False)
    image_url_l = models.URLField(blank=False)

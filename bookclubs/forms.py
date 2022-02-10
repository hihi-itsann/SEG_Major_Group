from django import forms
from django.core.validators import RegexValidator
from .models import User, Club, Application, Role, Post, Comment, Rating
from django.contrib.auth import authenticate
# from django.forms.widgets import DateInput
from django.db import IntegrityError
import datetime


from .models import Post
#from django.forms.widgets import DateInput


class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """ Ensure that new_password and password_confirmation contain the same password."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'bio', 'dob', 'gender', 'location',
                  'meeting_preference']
        widgets = {'bio': forms.Textarea()}

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            bio=self.cleaned_data.get('bio'),
            password=self.cleaned_data.get('new_password'),
            dob=self.cleaned_data.get('dob'),
            gender=self.cleaned_data.get('gender'),
            location=self.cleaned_data.get('location'),
            meeting_preference=self.cleaned_data.get('meeting_preference'),
        )
        return user


class LogInForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'bio', 'dob', 'gender', 'location',
                  'meeting_preference']
        widgets = {'bio': forms.Textarea()}


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""

        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class RateForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rate']


class NewClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['club_name', 'meeting_status', 'location', 'public_status', 'genre', 'description']
        widgets = {'description': forms.Textarea()}

    MEETING_STATUS_CHOICES = (
        (True, 'In Person'),
        (False, 'Online')
    )
    PUBLIC_STATUS_CHOICES = (
        (True, 'Public'),
        (False, 'Private')
    )

    meeting_status = forms.ChoiceField(widget=forms.Select(), label='Meetings Held', choices=MEETING_STATUS_CHOICES)
    public_status = forms.ChoiceField(widget=forms.Select(), label='Status', choices=PUBLIC_STATUS_CHOICES)

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()

    def save(self):
        """Create a new club."""
        super().save(commit=False)
        club = Club.objects.create(
            club_name=self.cleaned_data.get('club_name'),
            meeting_status=self.cleaned_data.get('meeting_status'),
            location=self.cleaned_data.get('location'),
            public_status=self.cleaned_data.get('public_status'),
            genre=self.cleaned_data.get('genre'),
            description=self.cleaned_data.get('description')
        )
        return club


class NewApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['statement']

    def save(self, user=None, club=None):
        super().save(commit=False)
        application = Application.objects.create(
            user=user,
            club=club,
            statement=self.cleaned_data.get('statement'),
            status='pending'
        )
        return application


class UpdateApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['statement']

    def save(self, past_id=None, user=None, club=None):
        super().save(commit=False)
        delete_application = Application.objects.get(id=past_id)
        delete_application.delete()
        application = Application.objects.create(
            id=past_id,
            user=user,
            club=club,
            statement=self.cleaned_data.get('statement'),
            status='pending'
        )
        return application


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'author', 'body')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Which was the name of the book that you just finished?'}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'What are your thoughts?'}),

        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

        widgets = {
            'body': forms.Textarea(),
        }

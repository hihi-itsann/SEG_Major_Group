from django import forms
from django.core.validators import RegexValidator
from .models import User, Club, Application, Role, Post, Comment, BookRatingReview, Meeting, MeetingAttendance, Book
from django.contrib.auth import authenticate
# from django.forms.widgets import DateInput
from django.db import IntegrityError
from django.utils import timezone
from .models import Post

# from django.forms.widgets import DateInput


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

def validate_date_not_in_future(value):
        if value <= timezone.now().date():
            raise forms.ValidationError('date needs to be in the future')
def validate_date_not_in_past(value):
        if value >= timezone.now().date():
            raise forms.ValidationError('Date needs to be in the past')


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    dob=forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),validators=[validate_date_not_in_past])

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'bio', 'dob', 'gender', 'location', 'city', 'country',
                  'meeting_preference']
        widgets = { 'bio': forms.Textarea()}

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
    dob=forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),validators=[validate_date_not_in_past])


    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'bio', 'dob', 'gender', 'location', 'city', 'country',
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


class RateReviewForm(forms.ModelForm):
    class Meta:
        model = BookRatingReview
        fields = ['rate', 'review']
        widgets = {
            'review': forms.Textarea(),
        }


class ClubForm(forms.ModelForm):
    """Create and update club form"""

    class Meta:
        model = Club
        fields = ['club_name', 'meeting_status', 'location', 'city', 'country', 'public_status', 'genre', 'description']
        widgets = {'description': forms.Textarea()}

    MEETING_CHOICES = (
        ('ONL', 'Online'),
        ('OFF', 'In-person')
    )
    PRIVACY_CHOICES = (
        ('PUB', 'Public'),
        ('PRI', 'Private')
    )

    GENRE_CHOICES = [('Fiction', 'Fiction'), ('Non-Fiction', 'Non-Fiction')]
    #GENRE_CHOICES = Book.get_genres()


    meeting_status = forms.ChoiceField(widget=forms.Select(), label='Meetings Held', choices=MEETING_CHOICES)
    public_status = forms.ChoiceField(widget=forms.Select(), label='Status', choices=PRIVACY_CHOICES)
    genre = forms.ChoiceField(widget=forms.Select(), choices=GENRE_CHOICES)

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['statement']
        widgets = {'statement': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Why do you want to '
                                                                                              'join this club?'}), }

    def original_save(self, user=None, club=None):
        super().save(commit=False)
        application = Application.objects.create(
            user=user,
            club=club,
            statement=self.cleaned_data.get('statement'),
            status='P'
        )
        return application


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'author','club', 'body')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'What is the name of the book that you just finished?'}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'club': forms.Select(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'What are your thoughts?'}),

        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

        widgets = {
            'body': forms.Textarea(),
        }


class MeetingForm(forms.ModelForm):

    date=forms.DateField(
    widget=forms.SelectDateWidget(),
    initial=timezone.now().date(),
    validators=[validate_date_not_in_future]
    )

    class Meta:
        model = Meeting
        fields = ('topic', 'description', 'location', 'date', 'time_start', 'duration')

        widgets = {
            'topic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Topic'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Agenda'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            #'date': forms.DateInput(attrs={'class': 'form-control', 'format': "%Y-%m-%d", 'placeholder': 'yyyy-mm-dd'}),
            'time_start': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'hh:mm'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutes'})
        }

    def original_save(self, user=None, club=None, book=None, join_link=None, start_link=None):
        super().save(commit=False)
        meeting = Meeting.objects.create(
            club=club,
            book=book,
            topic=self.cleaned_data.get('topic'),
            description=self.cleaned_data.get('description'),
            meeting_status=club.meeting_status,
            location=self.cleaned_data.get('location'),
            date=self.cleaned_data.get('date'),
            time_start=self.cleaned_data.get('time_start'),
            duration=self.cleaned_data.get('duration'),
            join_link=join_link,
            start_link=start_link
        )
        host = MeetingAttendance.objects.create(
            user=user,
            meeting=meeting,
            meeting_role='H'
        )
        return meeting

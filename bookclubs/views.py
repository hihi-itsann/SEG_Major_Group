from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User, Club, Role, Application
from django.shortcuts import redirect, render
from bookclubs.helpers import login_prohibited
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from bookclubs.forms import SignUpForm, LogInForm, UserForm, PasswordForm, NewClubForm, NewApplicationForm, UpdateApplicationForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from bookclubs.models import User
from django.views import View
from django.utils.decorators import method_decorator
from django.conf import settings
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.urls import reverse
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import MultipleObjectMixin
from .helpers import *
from django.db import IntegrityError


@login_prohibited
def home(request):
    return render(request, 'home.html')


@login_required
def feed(request):
    return render(request, 'feed.html')


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class SignUpView(LoginProhibitedMixin, FormView):
    """View that signs up user."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class LogInView(LoginProhibitedMixin, View):
    """View that handles log in."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = 'feed'

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    logout(request)
    return redirect('home')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update logged-in user's profile."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class PasswordView(LoginRequiredMixin, FormView):
    """View that handles password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    @property
    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


@login_required
def create_club(request):
    """a logged in user can create a club"""
    if request.method == 'POST':
        form = NewClubForm(request.POST)
        if form.is_valid():
            club = form.save()
            club.club_members.add(request.user, through_defaults={'club_role': 'OWN'})
            return redirect('feed')
    else:
        form = NewClubForm()
    return render(request, 'new_club.html', {'form': form})


@login_required
@club_exists
@membership_required
def club_feed(request, club_name):
    is_officer = False
    is_owner = False
    current_club = Club.objects.get(club_name=club_name)
    club_role = current_club.get_club_role(request.user)
    members = current_club.get_members()
    management = current_club.get_management()
    number_of_applicants = current_club.get_applicants().count()
    if club_role == 'OWN':
        is_owner = True
    elif club_role == 'OFF':
        is_officer = True
    return render(request, 'club_feed.html',
                  {'club': current_club, 'is_officer': is_officer, 'is_owner': is_owner, 'members': members,
                   'management': management, 'number_of_applicants': number_of_applicants})


@login_required
@club_exists
def club_welcome(request, club_name):
    is_applicant = False
    is_member = False
    is_banned = False
    club = Club.objects.get(club_name=club_name)
    user = request.user
    try:
        club_role = club.get_club_role(user)
    except Role.DoesNotExist:
        return render(request, 'club_welcome.html',
                      {'club': club, 'user': user, 'is_applicant': is_applicant, 'is_member': is_member,
                       'is_banned': is_banned})
    else:
        if club_role == 'APP':
            is_applicant = True
        elif club_role == 'BAN':
            is_banned = True
        elif club_role == 'MEM' or club_role == 'OWN' or club_role == 'OFF':
            is_member = True
    return render(request, 'club_welcome.html',
                  {'club': club, 'user': user, 'is_applicant': is_applicant, 'is_member': is_member,
                   'is_banned': is_banned})


"""only login user can create new club"""


@login_required
def create_club(request):
    if request.method == 'POST':
        form = NewClubForm(request.POST)
        if form.is_valid():
            club = form.save()
            club.club_members.add(request.user, through_defaults={'club_role': 'OWN'})
            return redirect('feed')
    else:
        form = NewClubForm()
    return render(request, 'new_club.html', {'form': form})


@login_required
@club_exists
@owner_required
def delete_club(request, club_name):
    current_club = Club.objects.get(club_name=club_name)
    current_club.delete()
    return feed(request)


@login_required
@club_exists
@membership_prohibited
def new_application(request, club_name):
    current_club = Club.objects.get(club_name=club_name)
    if request.method == 'POST':
        form = NewApplicationForm(request.POST)
        if form.is_valid():
            try:
                application = form.save(request.user, current_club)
                current_club.club_members.add(request.user, through_defaults={'club_role': 'APP'})
                messages.add_message(request, messages.SUCCESS, "Application submitted!")
                return redirect('feed')
            except IntegrityError as e:
                messages.add_message(request, messages.WARNING,
                                     "Cannot submit a new application to this club. Please edit your current "
                                     "application.")
                return redirect('feed')
    else:
        form = NewApplicationForm()
    return render(request, 'new_application.html', {'form': form, 'club_name': club_name})


@login_required
@membership_prohibited
def edit_application(request, club_name):
    """Deletes current application and replaces it with another applcation with updated statement"""
    club_applied = Club.objects.get(club_name=club_name)
    application = Application.objects.get(user=request.user, club=club_applied)
    application_id = application.id
    form = UpdateApplicationForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save(application_id, request.user, club_applied)
            messages.add_message(request, messages.SUCCESS, "Application edited successfully!")
            return redirect('feed')
    return render(request, 'edit_application.html', {'form': form, 'club_name': club_name})

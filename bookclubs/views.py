from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User, Club, Role, Application, Post, Comment
from django.shortcuts import redirect, render
from bookclubs.helpers import login_prohibited
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from bookclubs.forms import SignUpForm, LogInForm, UserForm, PasswordForm, NewClubForm, NewApplicationForm, UpdateApplicationForm, PostForm
from django.urls import reverse, reverse_lazy
from bookclubs.forms import SignUpForm, LogInForm, UserForm, PasswordForm
from django.urls import reverse
from bookclubs.forms import SignUpForm, LogInForm, UserForm, PasswordForm, NewClubForm, NewApplicationForm, UpdateApplicationForm
from bookclubs.forms import SignUpForm, LogInForm, UserForm, PasswordForm, NewClubForm, NewApplicationForm, UpdateApplicationForm, PostForm, CommentForm
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
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import MultipleObjectMixin
from .helpers import *
from django.db import IntegrityError

from .models import Post
from .forms import PostForm
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
@non_applicant_required
def new_application(request, club_name):
    current_club = Club.objects.get(club_name=club_name)
    if request.method == 'POST':
        form = NewApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(request.user, current_club)
            current_club.club_members.add(request.user, through_defaults={'club_role': 'APP'})
            messages.add_message(request, messages.SUCCESS, "Application submitted!")
            return redirect('feed')
    else:
        form = NewApplicationForm()
    return render(request, 'new_application.html', {'form': form, 'club_name': club_name})


@login_required
@club_exists
@applicant_required
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


@login_required
@club_exists
@applicant_required
def withdraw_application(request, club_name):
    club_applied = Club.objects.get(club_name=club_name)
    try:
        Application.objects.get(user=request.user, club=club_applied).delete()
        Role.objects.get(user=request.user, club=club_applied).delete()
        messages.add_message(request, messages.SUCCESS, "Application withdrawn.")
        return redirect('feed')
    except Application.DoesNotExist:
        messages.add_message(request, messages.WARNING, "No application submitted for this club.")
    return render(request, 'edit_application.html', {'club_name': club_name})

@login_required
@club_exists
@management_required
def applicants_list(request,club_name):
        is_empty = False
        current_club = Club.objects.get(club_name=club_name)
        applicants = current_club.get_applicants()
        if applicants.count() == 0:
            is_empty = True
        return render(request,'applicants_list.html', {'applicants':applicants,'is_empty':is_empty, 'current_club':current_club})

@login_required
@club_exists
@management_required
def accept_applicant(request,club_name,user_id):
        current_club = Club.objects.get(club_name=club_name)
        try:
            applicant = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'APP')
            current_club.toggle_member(applicant)
        except (ObjectDoesNotExist):
            return redirect('feed')

        else:
            return applicants_list(request,current_club.club_name)

@login_required
@club_exists
@management_required
def reject_applicant(request,club_name,user_id):
        current_club = Club.objects.get(club_name=club_name)
        try:
            applicant = User.objects.get(id=user_id,club__club_name = current_club.club_name, role__club_role = 'APP')
            current_club.remove_user_from_club(applicant)
        except ObjectDoesNotExist:
            return redirect('feed')
        else:
            return applicants_list(request,current_club.club_name)

@login_required
def my_clubs(request):
    clubs = Role.objects.filter(user=request.user)
    return render(request, 'my_clubs.html', {'clubs': clubs})

@login_required
def club_list(request):
    clubs = []
    if Role.objects.filter(user=request.user):
        relations = Role.objects.filter(user=request.user)
        clubs = Club.objects.all()
        for club in relations:
            clubs = clubs.exclude(club_name=club.club.club_name)
    else:
        clubs = Club.objects.all()
    return render(request, 'club_list.html', {'clubs': clubs})

@login_required
def my_applications(request):
    applications = Application.objects.filter(user=request.user)
    return render(request, 'my_applications.html', {'applications': applications})
    return reverse('feed')

class FeedView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'feed.html'
    ordering = ['-post_date','-post_datetime',]

class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'create_post.html'

class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('feed')

class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'create_comment.html'
    success_url = reverse_lazy('feed')

    def form_valid(self,form):
        form.instance.related_post_id= self.kwargs['pk']
        form.instance.author= self.request.user
        return super().form_valid(form)

class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'delete_comment.html'
    success_url = reverse_lazy('feed')

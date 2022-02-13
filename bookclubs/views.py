from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.shortcuts import redirect, render, get_object_or_404
from bookclubs.forms import SignUpForm, LogInForm, UserForm, PasswordForm, NewClubForm, NewApplicationForm, \
    UpdateApplicationForm, CommentForm, RateForm, PostForm
from .helpers import *
from .models import User, Book, Application, Comment, Post, Rating


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


@login_required
def show_user(request, username):
    if User.objects.filter(username=username).count() == 1:
        user = User.objects.get(username=username)
        return render(request, 'show_user.html', {'user': user})
    else:
        messages.add_message(request, messages.WARNING, "User not found.")
        return redirect('feed')


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


class BookListView(LoginRequiredMixin, ListView):
    """View that shows a list of all books"""
    model = Book
    template_name = 'book_list.html'
    context_object_name = "books"


class ShowBookView(LoginRequiredMixin, DetailView):
    """View that shows book details."""
    model = Book
    template_name = 'show_book.html'
    pk_url_kwarg = 'ISBN'

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to book_list if ISBN invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('book_list')


class CreateBookRateView(LoginRequiredMixin, CreateView):
    model = Rating
    form_class = RateForm
    template_name = 'create_book_rating.html'

    def form_valid(self, form):
        """Process a valid form."""
        form.instance.user = self.request.user
        form.instance.book_id = self.kwargs['ISBN']
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('book_list')

    def handle_no_permission(self):
        return redirect('log_in')


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
    if club_role == 'OWN':
        is_owner = True
    elif club_role == 'OFF':
        is_officer = True
    return render(request, 'club_feed.html',
                  {'club': current_club, 'is_officer': is_officer, 'is_owner': is_owner, 'members': members,
                   'management': management})


@login_required
@club_exists
def club_welcome(request, club_name):
    is_member = False
    is_banned = False
    club = Club.objects.get(club_name=club_name)
    user = request.user
    try:
        club_role = club.get_club_role(user)
    except Role.DoesNotExist:
        return render(request, 'club_welcome.html',
                      {'club': club, 'user': user, 'is_member': is_member,
                       'is_banned': is_banned})
    else:
        if club_role == 'BAN':
            is_banned = True
        elif club_role == 'MEM' or club_role == 'OWN' or club_role == 'OFF':
            is_member = True
    return render(request, 'club_welcome.html',
                  {'club': club, 'user': user, 'is_member': is_member,
                   'is_banned': is_banned})


@login_required
def create_club(request):
    """a user can create a club"""
    if request.method == 'POST':
        form = NewClubForm(request.POST)
        if form.is_valid():
            club = form.save()
            club.club_members.add(request.user, through_defaults={'club_role': 'OWN'})
            return redirect('feed')
    else:
        form = NewClubForm()
    return render(request, 'create_club.html', {'form': form})


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
def create_application(request, club_name):
    """Creates a new application, automatically accepted if club is public"""
    current_club = Club.objects.get(club_name=club_name)
    if request.method == 'POST':
        form = NewApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(request.user, current_club)
            if current_club.public_status:
                current_club.club_members.add(request.user, through_defaults={'club_role': 'MEM'})
                current_club.toggle_member(request.user)
                application.change_status('A')
            else:
                application.change_status('P')
            messages.add_message(request, messages.SUCCESS, "Application submitted!")
            return redirect('my_applications')
    else:
        form = NewApplicationForm()
    return render(request, 'create_application.html', {'form': form, 'club_name': club_name})


@login_required
@club_exists
@applicant_required
def edit_application(request, club_name):
    """Deletes current application and replaces it with another application with updated statement"""
    club_applied = Club.objects.get(club_name=club_name)
    application = Application.objects.get(user=request.user, club=club_applied)
    application_id = application.id
    form = UpdateApplicationForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save(request.user, club_applied)
            messages.add_message(request, messages.SUCCESS, "Application edited successfully!")
            return redirect('my_applications')
    return render(request, 'edit_application.html', {'form': form, 'club_name': club_name})


@login_required
@club_exists
@applicant_required
def withdraw_application(request, club_name):
    """Deletes an application to a club"""
    club_applied = Club.objects.get(club_name=club_name)
    Application.objects.get(user=request.user, club=club_applied).delete()
    messages.add_message(request, messages.SUCCESS, "Application withdrawn.")
    return redirect('my_applications')


@login_required
def my_applications(request):
    """Shows all the applications that the user has submitted"""
    applications = Application.objects.filter(user=request.user)
    applications_count = applications.count()
    return render(request, 'my_applications.html',
                  {'applications': applications, 'applications_count': applications_count})


# TODO: Fix data shown
@login_required
@club_exists
@management_required
def application_list(request, club_name):
    """Shows all the pending applications to club management"""
    current_club = Club.objects.get(club_name=club_name)
    applications = Application.objects.filter(club=current_club, status='P')
    applications_count = applications.count()
    return render(request, 'application_list.html',
                  {'current_club': current_club, 'applications': applications,
                   'applications_count': applications_count})


@login_required
@club_exists
@management_required
def accept_applicant(request, club_name, user_id):
    """Changes application status to Accepted and adds user to the club as a member"""
    current_club = Club.objects.get(club_name=club_name)
    user = User.objects.get(id=user_id)
    application = Application.objects.get(user=user, club=current_club)
    application.change_status('A')
    Role.objects.create(user=user, club=current_club, club_role='MEM')
    return redirect(f'/club/{club_name}/applications/')


@login_required
@club_exists
@management_required
def reject_applicant(request, club_name, user_id):
    """Changes application status to Rejected"""
    current_club = Club.objects.get(club_name=club_name)
    user = User.objects.get(id=user_id)
    application = Application.objects.get(user=user, club=current_club)
    application.change_status('R')
    return redirect(f'/club/{club_name}/applications/')


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


class PostCommentView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'post_comment.html'
    ordering = ['-post_date', '-post_datetime', ]


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'create_post.html'
    success_url = reverse_lazy('post_comment')


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('post_comment')


class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'create_comment.html'
    success_url = reverse_lazy('post_comment')

    def form_valid(self, form):
        form.instance.related_post_id = self.kwargs['pk']
        form.instance.author = self.request.user
        return super().form_valid(form)


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'delete_comment.html'
    success_url = reverse_lazy('post_comment')

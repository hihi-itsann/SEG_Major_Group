from ntpath import join
# from os import startfile
from django.contrib import messages
from webbrowser import get
from django.db.models import Q  # filter exception
from django.db.models import F
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.shortcuts import redirect, render, get_object_or_404, HttpResponseRedirect
from bookclubs.forms import SignUpForm, LogInForm, UserForm, PasswordForm, ClubForm, ApplicationForm, CommentForm, \
    RateReviewForm, PostForm, MeetingForm, ApplicationForm
from .helpers import *
from .models import User, Book, Application, Vote, Comment, Post, BookRatingReview, BookStatus, Club, Meeting, \
    MeetingAttendance
from django.core.paginator import Paginator
from random import choice
from bookclubs.meeting_link import create_zoom_meeting, get_join_link, get_start_link
from datetime import datetime
from bookclubs.recommender.keras import get_recommendations


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


# ----------------------------------book functions-----------------------------------

class BookListView(LoginRequiredMixin, ListView):
    """View that shows a list of all books"""
    model = Book
    template_name = 'book_list.html'
    context_object_name = "books"
    paginate_by = settings.BOOKS_PER_PAGE
    pk_url_kwarg = 'book_genre'

    def get_queryset(self):
        if self.kwargs['book_genre'] == 'All':
            return Book.objects.all()
        return Book.objects.filter(genre=self.kwargs['book_genre'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = Book.objects.all()
        genres = []
        for book in books:
            genres.append(book.genre)
        genres = list(set(genres))
        context['genres'] = genres
        return context


class ShowBookView(LoginRequiredMixin, DetailView):
    """View that shows book details."""
    model = Book
    template_name = 'show_book.html'
    pk_url_kwarg = 'ISBN'

    def get_context_data(self, **kwargs):
        book = self.get_object()
        context = super().get_context_data(**kwargs)
        try:
            bookStatus = BookStatus.objects.get(user=self.request.user, book=book)
        except ObjectDoesNotExist:
            context['readingStatus'] = 'U'  # default is U (unread)
            context['isInReadingList'] = False
        else:
            # context['readingStatus'] = book.getReadingStatus(self.request.user)
            context['readingStatus'] = bookStatus.status
            context['isInReadingList'] = True
            context['form'] = RateReviewForm()
        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to book_list if ISBN invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('book_list', 'All')


class CreateBookRateReviewView(LoginRequiredMixin, CreateView):
    model = BookRatingReview
    form_class = RateReviewForm
    template_name = 'show_book.html'
    http_method_names = ['post']
    pk_url_kwarg = 'ISBN'

    def form_valid(self, form):
        """Process a valid form."""
        form.instance.user = self.request.user
        form.instance.book_id = self.kwargs['ISBN']
        return super().form_valid(form)

    def get_success_url(self):
        book = Book.objects.get(ISBN=self.kwargs['ISBN'])
        return '{}#education'.format(reverse('show_book', kwargs={'ISBN': book.ISBN}))


@login_required
@book_exists
@own_feedback_exists
def delete_book_rating_review(request, ISBN, pk):
    book = Book.objects.get(ISBN=ISBN)
    rating_review = BookRatingReview.objects.get(book=book, id=pk, user=request.user)
    rating_review.delete();
    messages.add_message(request, messages.SUCCESS, "This review has successfully been deleted!")
    return redirect('show_book', ISBN)


@login_required
@book_exists
@bookStatus_does_not_exists
def create_book_status(request, ISBN):
    book = Book.objects.get(ISBN=ISBN)
    bookStatus = BookStatus.objects.create(book=book, user=request.user)
    messages.add_message(request, messages.SUCCESS, "Add to your reading list successfully!")
    return redirect('reading_book_list', 'All')


@login_required
@book_exists
@bookStatus_exists
def delete_book_status(request, ISBN):
    book = Book.objects.get(ISBN=ISBN)
    current_book_status = BookStatus.objects.get(user=request.user, book=book)
    current_book_status.delete()
    messages.add_message(request, messages.SUCCESS, "The Book has already been deleted in your reading list!")
    return redirect('reading_book_list', 'All')


@login_required
@book_exists
@bookStatus_exists
def change_book_status(request, ISBN, choice):
    current_book = Book.objects.get(ISBN=ISBN)
    current_book_status = BookStatus.objects.get(user=request.user, book=current_book)
    current_book_status.change_status(choice)
    messages.add_message(request, messages.SUCCESS,
                         f'Successfully change the book status to {current_book_status.get_status_display()}!')
    return redirect('show_book', ISBN)


@login_required
def reading_book_list(request, book_genre='All'):
    bookStatuses = BookStatus.objects.filter(user=request.user)
    genres = []
    for bookStatus in bookStatuses:
        genres.append(bookStatus.book.genre)
    genres = list(set(genres))
    unreadBookStatuses = bookStatuses.filter(status='U')
    readingBookStatuses = bookStatuses.filter(status='R')
    finishedBookStatuses = bookStatuses.filter(status='F')
    unreadBooks = []
    readingBooks = []
    finishedBooks = []
    for bookStatus in unreadBookStatuses:
        if bookStatus.book.genre == book_genre or book_genre == 'All':
            unreadBooks.append(bookStatus.book)
    for bookStatus in readingBookStatuses:
        if bookStatus.book.genre == book_genre or book_genre == 'All':
            readingBooks.append(bookStatus.book)
    for bookStatus in finishedBookStatuses:
        if bookStatus.book.genre == book_genre or book_genre == 'All':
            finishedBooks.append(bookStatus.book)
    args = {'unreadBooks': unreadBooks, 'readingBooks': readingBooks, 'finishedBooks': finishedBooks, 'genres': genres}
    return render(request, 'reading_book_list.html', args)


# --------------------------application functions---------------------------------


@login_required
@club_exists
@non_applicant_required
def create_application(request, club_name):
    """Creates a new application, automatically accepted if club is public"""
    current_club = Club.objects.get(club_name=club_name)
    if current_club.public_status == 'PUB':
        current_club.club_members.add(request.user, through_defaults={'club_role': 'MEM'})
        current_club.toggle_member(request.user)
        application = Application.objects.create(user=request.user, club=current_club, statement=' ', status='A')
        messages.add_message(request, messages.SUCCESS, "Club is public. You are now a member!")
        return redirect('my_applications')
    else:
        if request.method == 'POST':
            form = ApplicationForm(request.POST)
            if form.is_valid():
                application = form.original_save(request.user, current_club)
                application.change_status('P')
                messages.add_message(request, messages.SUCCESS, "Application submitted!")
                return redirect('my_applications')
        else:
            form = ApplicationForm()
        return render(request, 'create_application.html', {'form': form, 'club_name': club_name})


@login_required
@club_exists
@applicant_required
def edit_application(request, club_name):
    """Deletes current application and replaces it with another application with updated statement"""
    club_applied = Club.objects.get(club_name=club_name)
    application = Application.objects.get(user=request.user, club=club_applied)
    form = ApplicationForm(instance=application)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
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


# ----------------------------club functions---------------------------------------

@login_required
@club_exists
@membership_required
def club_feed(request, club_name):
    is_moderator = False
    is_owner = False
    current_club = Club.objects.get(club_name=club_name)
    club_role = current_club.get_club_role(request.user)
    members = current_club.get_members()
    management = current_club.get_management()
    posts = Post.objects.all().filter(club=current_club)
    if club_role == 'OWN':
        is_owner = True
    elif club_role == 'MOD':
        is_moderator = True
    return render(request, 'club_feed.html',
                  {'club': current_club, 'is_moderator': is_moderator, 'is_owner': is_owner, 'members': members,
                   'management': management, 'posts': posts})


@login_required
def create_club(request):
    """a user can create a club"""
    if request.method == 'POST':
        form = ClubForm(request.POST)
        if form.is_valid():
            club = form.save()
            club.club_members.add(request.user, through_defaults={'club_role': 'OWN'})
            return redirect('club_feed', club.club_name)
    else:
        form = ClubForm()
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
@membership_required
def leave_club(request, club_req):
    club = Club.objects.get(club_name=club_req)
    user = request.user
    cur_role = Role.objects.get(club=club, user=user)
    number_owner_club = Role.objects.filter(club=club, club_role='OWN').count()
    # print(number_owner_club)
    if cur_role.club_role == 'OWN' and (number_owner_club == 1):
        messages.warning(request,
                         'Owner cannot leave, if the club has only 1 owner!!! You can transfer owner to others.')
        return redirect('member_list', club_name=club.club_name)
    else:
        Role.objects.filter(user=request.user, club=club).delete()
        messages.success(request, f'You have now left the club {club.club_name}.')
        return redirect('my_clubs')


@login_required
@club_exists
@owner_required
def update_club_info(request, club_name):
    """owner can change information of club"""
    club = Club.objects.get(club_name=club_name)
    form = ClubForm(instance=club)
    if request.method == 'POST':
        form = ClubForm(request.POST, instance=club)
        if form.is_valid():
            club = form.save()
            return redirect('club_feed', club.club_name)
    return render(request, 'update_club_info.html', {'form': form, 'club_name': club_name})


@login_required
def my_clubs(request):
    clubs = Role.objects.filter(~Q(club_role='BAN'), user=request.user)
    return render(request, 'my_clubs.html', {'clubs': clubs})


@login_required
def club_list(request):
    clubs = []
    club_count = Club.objects.all().count()

    if Role.objects.filter(user=request.user):
        relations = Role.objects.filter(user=request.user)
        clubs = Club.objects.all()
        for club in relations:
            clubs = clubs.exclude(club_name=club.club.club_name)
    else:
        clubs = Club.objects.all()
    user_country = request.user.country
    user_city = request.user.city
    is_suitable_clubs = True
    distance = "all places"
    # print(city_list)
    meeting_status = request.user.meeting_preference

    if request.method == "POST":
        meeting_status = request.POST.get("meeting_status")
    if meeting_status == "Online" or meeting_status == "O":
        meeting_status = "Online"
        clubs = clubs.filter(meeting_status='ONL')
    elif meeting_status == "In person" or meeting_status == "P":
        meeting_status = "In person"

        clubs = clubs.filter(meeting_status='OFF')
        if request.method == "POST":
            distance = request.POST.get("distance")
        if distance == "same city":
            clubs = clubs.filter(city=user_city)
        elif distance == "same country":
            clubs = clubs.filter(country=user_country)
    if clubs.count() == 0:
        is_suitable_clubs = False
    else:
        is_suitable_clubs = True

    return render(request, 'club_list.html', {'clubs': clubs, 'meeting_status': meeting_status,
                                              'distance': distance, 'club_count': club_count, 'user': request.user,
                                              'is_suitable_clubs': is_suitable_clubs})


@login_required
@club_exists
@owner_required
def ban_member(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        member = User.objects.get(id=user_id, club__club_name=current_club.club_name)
        current_club.ban_member(member)
        messages.add_message(request, messages.SUCCESS, f'You have banned {member.username}.')
    except (ObjectDoesNotExist):
        messages.add_message(request, messages.WARNING, "User doesn't exist")
        return redirect('member_list', club_name)
    else:
        return redirect('member_list', club_name)


@login_required
@club_exists
@owner_required
def unban_member(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        banned = User.objects.get(id=user_id, club__club_name=current_club.club_name)
        current_club.unban_member(banned)
        messages.add_message(request, messages.SUCCESS, f'You have unbanned {banned.username}.')
    except ObjectDoesNotExist:
        messages.add_message(request, messages.WARNING, "User doesn't exist")
        return redirect('member_list', club_name)
    else:
        return redirect('member_list', club_name)


@login_required
@club_exists
@management_required
def remove_member(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    current_user_role = Role.objects.get(club=current_club, user=request.user).club_role
    try:
        member = User.objects.get(id=user_id, club__club_name=current_club.club_name)
        member_role = Role.objects.get(club=current_club, user=member).club_role
        if current_user_role == 'MOD' and member_role == 'MOD':
            messages.add_message(request, messages.WARNING, "Moderators can't remove each other!")
            return redirect('member_list', club_name)
        else:
            current_club.remove_user_from_club(member)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.WARNING, "User doesn't exist")
        return redirect('member_list', club_name)
    else:
        return redirect('member_list', club_name)


@login_required
@club_exists
@owner_required
def transfer_ownership(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        moderator = User.objects.get(id=user_id, club__club_name=current_club.club_name)
        current_club.transfer_ownership(request.user, moderator)
        messages.success(request, f'You have transferred owner privileges to {moderator.username}!')
    except (ObjectDoesNotExist):
        messages.add_message(request, messages.WARNING, "User doesn't exist")
        return redirect('member_list', club_name)
    else:
        return redirect('member_list', club_name)


@login_required
@club_exists
@owner_required
def demote_moderator(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        moderator = User.objects.get(id=user_id, club__club_name=current_club.club_name)
        current_club.toggle_member(moderator)
        messages.success(request, f'You have demoted {moderator.username} to the position of member!')
    except (ObjectDoesNotExist):
        messages.add_message(request, messages.WARNING, "User doesn't exist")
        return redirect('member_list', club_name)
    else:
        return redirect('member_list', club_name)


@login_required
@club_exists
@owner_required
def promote_member(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        changing_user = User.objects.get(id=user_id)
        current_club.toggle_moderator(changing_user)
        messages.success(request, f'You have promoted {changing_user.username} to the position of moderator!')
    except (ObjectDoesNotExist):
        messages.add_message(request, messages.WARNING, "User doesn't exist")
        return redirect('member_list', club_name)
    else:
        return redirect('member_list', club_name)


@login_required
@club_exists
@membership_required
def member_list(request, club_name):
    is_owner = False
    is_moderator = False
    current_club = Club.objects.get(club_name=club_name)
    current_user = request.user
    current_user_role = Role.objects.get(club=current_club, user=current_user).club_role
    if current_user_role == 'OWN':
        is_owner = True
    if current_user_role == 'MOD':
        is_moderator = True
    roles = Role.objects.filter(club=current_club)
    roles_num = roles.count()
    club_owner = Role.objects.get(club=current_club, club_role='OWN').user
    moderator_ids = Role.objects.filter(club=current_club, club_role='MOD').values_list('user', flat=True)
    club_moderators = User.objects.filter(id__in=moderator_ids)
    member_ids = Role.objects.filter(club=current_club, club_role='MEM').values_list('user', flat=True)
    club_members = User.objects.filter(id__in=member_ids)
    banned_ids = Role.objects.filter(club=current_club, club_role='BAN').values_list('user', flat=True)
    club_banned = User.objects.filter(id__in=banned_ids)
    context = {'club': current_club, 'current_user': current_user, 'current_user_role': current_user_role,
               'club_owner': club_owner, 'club_moderators': club_moderators, 'club_members': club_members,
               'club_banned': club_banned, 'is_owner': is_owner, 'is_moderator': is_moderator, 'roles': roles,
               'roles_num': roles_num}
    return render(request, 'member_list.html', context)


# -----------------------post and comment functions-------------------------------


@login_required
def post_upvote(request, post_id):
    user_upvoting = request.user
    post = Post.objects.get(id=post_id)
    club = Club.objects.get(id=post.club.id)
    post.toggle_upvote(user_upvoting)
    # The #post_id redirects to the part of the page with the post
    return redirect(f'/club/{club.club_name}/feed/#{post_id}')


@login_required
def post_downvote(request, post_id):
    user_downvoting = request.user
    post = Post.objects.get(id=post_id)
    club = Club.objects.get(id=post.club.id)
    post.toggle_downvote(user_downvoting)
    # The #post_id redirects to the part of the page with the post
    return redirect(f'/club/{club.club_name}/feed/#{post_id}')


class PostCommentView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'club_feed.html'


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'create_post.html'

    def form_valid(self, form):
        form.instance.club_id = self.kwargs['pk']
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        club = Club.objects.get(id=self.kwargs['pk'])
        return reverse('club_feed', kwargs={'club_name': club.club_name})


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'delete_post.html'

    def get_success_url(self):
        post = Post.objects.get(id=self.kwargs['pk'])
        club = Club.objects.get(id=post.club.id)
        return reverse('club_feed', kwargs={'club_name': club.club_name})


class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'create_comment.html'

    def form_valid(self, form):
        form.instance.related_post_id = self.kwargs['pk']
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        post = Post.objects.get(id=self.kwargs['pk'])
        club = Club.objects.get(id=post.club.id)
        return reverse('club_feed', kwargs={'club_name': club.club_name})


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'delete_comment.html'

    def get_success_url(self):
        comment = Comment.objects.get(id=self.kwargs['pk'])
        post = Post.objects.get(id=comment.related_post.id)
        club = Club.objects.get(id=post.club.id)
        return reverse('club_feed', kwargs={'club_name': club.club_name})


# --------------------meeting functions-----------------------------------------
import json
from django.core.serializers.json import DjangoJSONEncoder


@login_required
@club_exists
@membership_required
@not_last_host
def show_book_recommendations(request, club_name):
    """Choose a book for the meeting"""
    return render(request, "show_book_recommendations.html", {'club_name': club_name})


@login_required
@club_exists
@membership_required
@not_last_host
def show_book_recommendations_show(request, club_name):
    """Choose a book for the meeting"""
    current_club = Club.objects.get(club_name=club_name)
    recommendations = get_recommendations(current_club.id)

    if len(recommendations) == 0:
        recommended_books = []

    else:
        recommended_books = Book.objects.all().filter(ISBN__in=recommendations)

    data = dict()
    data['recommended_books'] = list(recommended_books.values())
    data['club_name'] = club_name
    # books=Book.objects.all().filter(ISBN='0060914068')
    # data = dict()
    # data['recommended_books'] = list(books.values())
    # data['club_name'] = club_name

    return JsonResponse(data)


@login_required
@club_and_book_exists
@membership_required
@not_last_host
def create_meeting(request, club_name, book_isbn):
    """Creates a new meeting within a club"""
    current_club = Club.objects.get(club_name=club_name)
    chosen_book = Book.objects.get(ISBN=book_isbn)
    form = MeetingForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            join_link = None
            start_link = None
            if current_club.get_meeting_status() == "Online":
                create_zoom_meeting(request.POST.get("date"), request.POST.get("time_start"),
                                    request.POST.get("duration"))
                join_link = get_join_link()
                start_link = get_start_link()

            form.original_save(request.user, current_club, chosen_book, join_link, start_link)
            messages.add_message(request, messages.SUCCESS, "Meeting set up!")

            return redirect('meeting_list', club_name)

    else:
        form = MeetingForm()
    return render(request, 'create_meeting.html',
                  {'form': form, 'club': current_club, 'book_isbn': book_isbn, 'book': chosen_book})


@login_required
@club_exists
@membership_required
def meeting_list(request, club_name):
    """Shows all current and future meetings to members of the club"""
    current_club = Club.objects.get(club_name=club_name)
    meetings = Meeting.objects.filter(club=current_club)
    current_date = datetime.now().date()
    club_meeting_ids = meetings.values_list('id', flat=True)
    current_meeting_ids = []
    past_meeting_ids = []
    for meeting_id in club_meeting_ids:
        meeting = Meeting.objects.get(id=meeting_id)
        if current_date > meeting.date:
            past_meeting_ids.append(meeting.id)
        else:
            current_meeting_ids.append(meeting.id)
    current_meetings = Meeting.objects.filter(id__in=current_meeting_ids)
    past_meetings = Meeting.objects.filter(id__in=past_meeting_ids)
    return render(request, 'meeting_list.html',
                  {'club_name': club_name, 'past_meetings': past_meetings, 'current_meetings': current_meetings})


@login_required
@club_and_meeting_exists
@membership_required
def show_meeting(request, club_name, meeting_id):
    """Show a meeting"""
    meeting = Meeting.objects.get(id=meeting_id)
    is_host = meeting.is_host(request.user)
    is_attendee_only = meeting.is_attendee_only(request.user)

    return render(request, 'show_meeting.html', {'meeting': meeting, 'club_name': club_name, 'is_host': is_host,
                                                 'is_attendee_only': is_attendee_only})


@login_required
@club_and_meeting_exists
@membership_required
def join_meeting(request, club_name, meeting_id):
    """User becomes an attendee of the meeting"""
    meeting = Meeting.objects.get(id=meeting_id)
    MeetingAttendance.objects.create(user=request.user, meeting=meeting, meeting_role='A')
    return redirect('meeting_list', club_name)


@login_required
@club_and_meeting_exists
@membership_required
def leave_meeting(request, club_name, meeting_id):
    """User stops being an attendee of the meeting"""
    meeting = Meeting.objects.get(id=meeting_id)
    MeetingAttendance.objects.get(user=request.user, meeting=meeting, meeting_role='A').delete()
    return redirect('meeting_list', club_name)


@login_required
@club_and_meeting_exists
@membership_required
@meeting_management_required
def delete_meeting(request, club_name, meeting_id):
    """Meeting is deleted"""
    meeting = Meeting.objects.get(id=meeting_id)
    MeetingAttendance.objects.filter(user=request.user, meeting=meeting).delete()
    meeting.delete()
    return redirect('meeting_list', club_name)


@login_required
@club_and_meeting_exists
@meeting_management_required
def edit_meeting(request, club_name, meeting_id):
    """Edit details of meeting"""
    current_club = Club.objects.get(club_name=club_name)
    meeting = Meeting.objects.get(id=meeting_id)
    form = MeetingForm(instance=meeting)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Meeting edited successfully!")
            return redirect('show_meeting', club_name, meeting_id)
    return render(request, 'edit_meeting.html', {'form': form, 'club_name': club_name, 'club': current_club,
                                                 'meeting': meeting, 'meeting_id': meeting_id})

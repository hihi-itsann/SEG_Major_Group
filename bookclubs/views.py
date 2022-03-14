from django.db.models import Q  # filter exception
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
    UpdateApplicationForm, CommentForm, RateReviewForm, PostForm, NewMeetingForm, UpdateClubForm
from .helpers import *
from .models import User, Book, Application, Comment, Post, BookRatingReview, BookStatus, Club, Meeting, \
    MeetingAttendance


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
    paginate_by = settings.BOOKS_PER_PAGE
    pk_url_kwarg = 'book_genre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = Book.objects.all()
        genres = []
        for book in books:
            genres.append(book.genre)
        genres = list(set(genres))
        if not self.kwargs['book_genre'] == 'All':
            context['books'] = Book.objects.filter(genre=self.kwargs['book_genre'])
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

    def get_context_data(self, **kwargs):
        book = Book.objects.get(ISBN=self.kwargs['ISBN'])
        context = super().get_context_data(**kwargs)
        context['book'] = book
        return context

    def get_success_url(self):
        book = Book.objects.get(ISBN=self.kwargs['ISBN'])
        return '{}#education'.format(reverse('show_book', kwargs={'ISBN': book.ISBN}))

@login_required
def delete_book_rating_review(request, ISBN, pk):
     book = Book.objects.get(ISBN=ISBN)
     try:
         rating_review=BookRatingReview.objects.get(book=book, id=pk)
     except ObjectDoesNotExist:
         messages.add_message(request, messages.ERROR, "You have not given that feedback!")
         return redirect('show_book', ISBN)
     rating_review.delete();
     messages.add_message(request, messages.SUCCESS, "This review has successfully been deleted!")
     return redirect('show_book', ISBN)


@login_required
def create_book_status(request, ISBN):
    book = Book.objects.get(ISBN=ISBN)
    try:
        bookStatus = BookStatus.objects.get(user=request.user, book=book)
    except ObjectDoesNotExist:
        bookStatus = BookStatus.objects.create(
            book=book,
            user=request.user,
        )
        messages.add_message(request, messages.SUCCESS, "Add to your reading list successfully!")
        return redirect('reading_book_list', 'All')
    messages.add_message(request, messages.ERROR, "The Book has already been added in your reading list!")
    return redirect('show_book', ISBN)


@login_required
def delete_book_status(request, ISBN):
    book = Book.objects.get(ISBN=ISBN)
    try:
        current_book_status = BookStatus.objects.get(user=request.user, book=book)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The Book is not in your reading list!")
        return redirect('show_book', ISBN)
    current_book_status.delete()
    messages.add_message(request, messages.ERROR, "The Book has already been deleted in your reading list!")
    return redirect('reading_book_list', 'All')


@login_required
def change_book_status(request, ISBN, choice):
    current_book = Book.objects.get(ISBN=ISBN)
    try:
        current_book_status = BookStatus.objects.get(user=request.user, book=current_book)
        current_book_status.change_status(choice)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, f'Unsuccessfully change the book status!')
        return redirect('show_book', ISBN)
    else:
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
            return redirect('club_feed', club.club_name)
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
@owner_required
def update_club_info(request, club_name):
    """owner change information of club"""
    club = Club.objects.get(club_name=club_name)
    form = UpdateClubForm(instance=club)
    if request.method == 'POST':
        form = UpdateClubForm(request.POST, instance=club)
        if form.is_valid():
            form.save()
            return redirect(f'/club/{club_name}/feed/')
    context = {'form': form}
    return render(request, 'update_club_info.html', context)


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
            if current_club.public_status == 'PUB':
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
    clubs = Role.objects.filter(~Q(club_role='BAN'), user=request.user)
    return render(request, 'my_clubs.html', {'clubs': clubs})


@login_required
def club_list(request):
    clubs = []
    if Club.objects.all().count()==0:
        club_exists=False
    else:
        club_exists=True

    if Role.objects.filter(user=request.user):
        relations = Role.objects.filter(user=request.user)
        clubs = Club.objects.all()
        for club in relations:
            clubs = clubs.exclude(club_name=club.club.club_name)
    else:
        clubs = Club.objects.all()
    user_country=request.user.country
    user_city=request.user.city
    is_suitable_clubs=True
    distance="all places"
    #print(city_list)
    meeting_status=request.user.meeting_preference

    if request.method=="POST":
        meeting_status=request.POST.get("meeting_status")
    if meeting_status == "Online" or meeting_status == "O":
        meeting_status="Online"
        clubs=clubs.filter(meeting_status='ONL')
    elif meeting_status=="In person" or meeting_status == "P":
        meeting_status="In person"

        clubs=clubs.filter(meeting_status='OFF')
        if request.method=="POST":
            distance=request.POST.get("distance")
        if distance == "same city":
            clubs=clubs.filter(city=user_city)
        elif distance=="same country":
            clubs=clubs.filter(country=user_country)
    if clubs.count()==0:
        is_suitable_clubs=False
    else:
        is_suitable_clubs=True

    return render(request, 'club_list.html', {'clubs': clubs,'meeting_status':meeting_status,
                            'distance':distance,'club_exists':club_exists,'is_suitable_clubs':is_suitable_clubs})


@login_required
@club_exists
@management_required
def members_management_list(request, club_name):
    banned_is_empty = False
    member_is_empty = False
    current_club = Club.objects.get(club_name=club_name)
    members = current_club.get_members()
    banned = current_club.get_banned_members()
    if members.count() == 0:
        member_is_empty = True
    if banned.count() == 0:
        banned_is_empty = True
    return render(request, 'member_management.html',
                  {'banned': banned, 'members': members, 'banned_is_empty': banned_is_empty,
                   'member_is_empty': member_is_empty, 'current_club': current_club})


@login_required
@club_exists
@management_required
def ban_member(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        member = User.objects.get(id=user_id, club__club_name=current_club.club_name, role__club_role='MEM')
        current_club.ban_member(member)
    except ObjectDoesNotExist:
        return redirect('feed')
    else:
        return members_management_list(request, current_club.club_name)


@login_required
@club_exists
@management_required
def unban_member(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        banned = User.objects.get(id=user_id, club__club_name=current_club.club_name, role__club_role='BAN')
        current_club.unban_member(banned)
    except ObjectDoesNotExist:
        return redirect('feed')
    else:
        return members_management_list(request, current_club.club_name)


@login_required
@club_exists
@management_required
def remove_member(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        member = User.objects.get(id=user_id, club__club_name=current_club.club_name, role__club_role='MEM')
        current_club.remove_user_from_club(member)
    except ObjectDoesNotExist:
        return redirect('feed')
    else:
        return members_management_list(request, current_club.club_name)


@login_required
@club_exists
@owner_required
def moderator_list(request, club_name):
    current_club = Club.objects.get(club_name=club_name)
    moderators = current_club.get_moderators()
    return render(request, 'moderator_list.html', {'moderators': moderators, 'current_club': current_club})


@login_required
@club_exists
@owner_required
def transfer_ownership(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        moderator = User.objects.get(id=user_id, club__club_name=current_club.club_name, role__club_role='MOD')
        current_club.transfer_ownership(request.user, moderator)
    except (ObjectDoesNotExist):
        return redirect('feed')
    else:
        return moderator_list(request, current_club.club_name)


@login_required
@club_exists
@owner_required
def demote_moderator(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        moderator = User.objects.get(id=user_id, club__club_name=current_club.club_name, role__club_role='MOD')
        current_club.toggle_member(moderator)
    except (ObjectDoesNotExist):
        return redirect('feed')
    else:
        return moderator_list(request, current_club.club_name)


@login_required
@club_exists
@management_required
def promote_member(request, club_name, user_id):
    current_club = Club.objects.get(club_name=club_name)
    try:
        member = User.objects.get(id=user_id, club__club_name=current_club.club_name, role__club_role='MEM')
        current_club.toggle_moderator(member)
    except (ObjectDoesNotExist):
        return redirect('feed')
    else:
        return members_management_list(request, current_club.club_name)


@login_required
@club_exists
@owner_required
def change_club_to_public_status(request, club_name):
    """Changes club status to private"""
    current_club = Club.objects.get(club_name=club_name)
    current_club.change_club_status(True)
    return redirect('feed')


@login_required
@club_exists
@membership_required
def member_list(request, club_name):
    is_owner = False
    club = Club.objects.get(club_name=club_name)
    cur_user = request.user
    roles = Role.objects.filter(club=club).exclude(club_role='BAN')
    club_role = club.get_club_role(cur_user)
    if club_role == 'OWN':
        is_owner = True
    context = {'club': club, 'roles': roles, 'is_owner': is_owner}
    return render(request, "member_list.html", context)


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


@login_required
@club_exists
@membership_required
def show_book_recommendations(request, club_name):
    """Choose a book for the meeting"""
    # current_club = Club.objects.get(club_name=club_name)
    all_books = Book.objects.all()
    ## get_club_books_average_rating()
    #recommendations = get_recommendations(current_club.id)
    #print(recommendations)
    #recommended_books = Book.objects.all().filter(ISBN__in=recommendations)

    return render(request, 'show_book_recommendations.html',
                  {'recommended_books': all_books, 'club_name': club_name})


@login_required
@club_and_book_exists
@membership_required
def create_meeting(request, club_name, book_isbn):
    """Creates a new meeting within a club"""
    current_club = Club.objects.get(club_name=club_name)
    chosen_book = Book.objects.get(ISBN=book_isbn)
    if request.method == 'POST':
        form = NewMeetingForm(request.POST)
        if form.is_valid():
            form.save(request.user, current_club, chosen_book)
            messages.add_message(request, messages.SUCCESS, "Meeting set up!")
            return redirect('meeting_list', club_name)
    else:
        form = NewMeetingForm()
    return render(request, 'create_meeting.html',
                  {'form': form, 'club_name': club_name, 'book_isbn': book_isbn, 'book': chosen_book})


@login_required
@club_exists
@membership_required
def meeting_list(request, club_name):
    """Shows all the meetings to members of the club"""
    current_club = Club.objects.get(club_name=club_name)
    meetings = Meeting.objects.filter(club=current_club)
    meetings_count = meetings.count()
    return render(request, 'meeting_list.html',
                  {'club_name': club_name, 'meetings': meetings,
                   'meetings_count': meetings_count})


@login_required
@membership_required
def show_meeting(request, club_name, meeting_id):
    """Show a meeting"""
    meeting = Meeting.objects.get(id=meeting_id)
    is_host = meeting.is_host(request.user)
    is_attendee_only = meeting.is_attendee_only(request.user)
    return render(request, 'show_meeting.html', {'meeting': meeting, 'club_name': club_name, 'is_host': is_host,
                                                 'is_attendee_only': is_attendee_only})


@login_required
@membership_required
def join_meeting(request, club_name, meeting_id):
    """User becomes an attendee of the meeting"""
    meeting = Meeting.objects.get(id=meeting_id)
    MeetingAttendance.objects.create(user=request.user, meeting=meeting, meeting_role='A')
    return redirect('meeting_list', club_name)


@login_required
@membership_required
def leave_meeting(request, club_name, meeting_id):
    """User stops being an attendee of the meeting"""
    meeting = Meeting.objects.get(id=meeting_id)
    MeetingAttendance.objects.get(user=request.user, meeting=meeting, meeting_role='A').delete()
    return redirect('meeting_list', club_name)


@login_required
@membership_required
def delete_meeting(request, club_name, meeting_id):
    """Meeting is deleted"""
    meeting = Meeting.objects.get(id=meeting_id)
    MeetingAttendance.objects.filter(user=request.user, meeting=meeting).delete()
    meeting.delete()
    return redirect('meeting_list', club_name)

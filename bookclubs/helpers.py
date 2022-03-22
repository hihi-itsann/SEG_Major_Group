from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from datetime import datetime

from .models import Club, Role, Application, Book, BookRatingReview, BookStatus, Meeting, MeetingAttendance


def login_prohibited(view_function):
    """check that the user is logged in"""

    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)

    return modified_view_function


def management_required(view_function):
    """check whether the user is an officer or the owner"""

    def modified_view_function(request, club_name, *args, **kwargs):
        current_club = Club.objects.get(club_name=club_name)
        if Role.objects.filter(user=request.user, club=current_club).count() == 1:
            role = Role.objects.get(user=request.user, club=current_club).club_role
            if role == 'BAN':
                messages.add_message(request, messages.WARNING, "You have been banned from this club!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            elif role == 'OWN' or role == 'MOD':
                return view_function(request, club_name, *args, **kwargs)
            else:
                messages.add_message(request, messages.WARNING, "You do not have the permissions required to access "
                                                                "this content!")
                return redirect(f'/club/{club_name}/feed/')
        else:
            messages.add_message(request, messages.WARNING, "You are not part of this club yet!")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    return modified_view_function


def meeting_management_required(view_function):
    """check whether the user is an attendee or the host"""

    def modified_view_function(request, club_name, meeting_id, *args, **kwargs):
        current_meeting = Meeting.objects.get(id=meeting_id)
        if MeetingAttendance.objects.filter(user=request.user, meeting=current_meeting).count() == 1:
            role = MeetingAttendance.objects.get(user=request.user, meeting=current_meeting).meeting_role
            if role == 'H':
                return view_function(request, club_name, meeting_id, *args, **kwargs)
            else:
                messages.add_message(request, messages.WARNING, "You are not the host and cannot delete this meeting!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            messages.add_message(request, messages.WARNING, "You are not part of this meeting yet!")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    return modified_view_function


def owner_required(view_function):
    """check whether the user is the owner"""

    def modified_view_function(request, club_name, *args, **kwargs):
        current_club = Club.objects.get(club_name=club_name)
        if Role.objects.filter(user=request.user, club=current_club).count() == 1:
            role = Role.objects.get(user=request.user, club=current_club).club_role
            if role == 'BAN':
                messages.add_message(request, messages.WARNING, "You have been banned from this club!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            elif role == 'OWN':
                return view_function(request, club_name, *args, **kwargs)
            else:
                messages.add_message(request, messages.WARNING, "You do not have the permissions required to access "
                                                                "this content!")
                return redirect(f'/club/{club_name}/feed/')
        else:
            messages.add_message(request, messages.WARNING, "You are not part of this club yet!")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    return modified_view_function


def membership_required(view_function):
    """check whether the user is a member"""

    def modified_view_function(request, club_name, *args, **kwargs):
        current_club = Club.objects.get(club_name=club_name)
        if Role.objects.filter(user=request.user, club=current_club).count() == 1:
            role = Role.objects.get(user=request.user, club=current_club).club_role
            if role == 'BAN':
                messages.add_message(request, messages.WARNING, "You have been banned from this club!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                return view_function(request, club_name, *args, **kwargs)
        else:
            messages.add_message(request, messages.WARNING, "You are not part of this club yet!")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    return modified_view_function


def non_applicant_required(view_function):
    """check to make sure user is not a member or an applicant"""

    def modified_view_function(request, club_name, *args, **kwargs):
        current_club = Club.objects.get(club_name=club_name)
        if Role.objects.filter(user=request.user, club=current_club).count() == 1:
            role = Role.objects.get(user=request.user, club=current_club).club_role
            if role == 'OWN':
                messages.add_message(request, messages.WARNING, "You are the owner!")
                return redirect(f'/club/{club_name}/feed/')
            elif role == 'BAN':
                messages.add_message(request, messages.WARNING, "You have been banned from this club!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                messages.add_message(request, messages.WARNING, "You are already a member!")
                return redirect(f'/club/{club_name}/feed/')
        if Application.objects.filter(user=request.user, club=current_club).count() == 1:
            application_status = Application.objects.get(user=request.user, club=current_club).status
            if application_status == 'R':
                messages.add_message(request, messages.WARNING, "You are not able to re-apply to this club.")
                return redirect('my_applications')
            elif application_status == 'A':
                messages.add_message(request, messages.WARNING, "Your application was accepted, however "
                                                                "something went wrong. You are now a member!")
                Role.objects.get_or_create(user=request.user, club=current_club, club_role='MEM')
                return redirect(f'/club/{club_name}/feed/')
            else:
                messages.add_message(request, messages.WARNING, "You have already applied for this club.")
                return redirect('my_applications')
        else:
            return view_function(request, club_name, *args, **kwargs)

    return modified_view_function


def applicant_required(view_function):
    """check to make sure user an applicant"""

    def modified_view_function(request, club_name, *args, **kwargs):
        current_club = Club.objects.get(club_name=club_name)
        if Role.objects.filter(user=request.user, club=current_club).count() == 1:
            role = Role.objects.get(user=request.user, club=current_club).club_role
            if role == 'OWN':
                messages.add_message(request, messages.WARNING, "You are the owner!")
                return redirect(f'/club/{club_name}/feed/')
            elif role == 'BAN':
                messages.add_message(request, messages.WARNING, "You have been banned from this club!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                messages.add_message(request, messages.WARNING, "You are already a member!")
                return redirect(f'/club/{club_name}/feed/')
        if Application.objects.filter(user=request.user, club=current_club).count() == 1:
            application_status = Application.objects.get(user=request.user, club=current_club).status
            if application_status == 'R':
                messages.add_message(request, messages.WARNING, "You are not able to edit your application to this "
                                                                "club.")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            elif application_status == 'A':
                messages.add_message(request, messages.WARNING, "Your application was accepted, however "
                                                                "something went wrong. You are now a member!")
                Role.objects.get_or_create(user=request.user, club=current_club, club_role='MEM')
                return redirect(f'/club/{club_name}/feed/')
            else:
                return view_function(request, club_name, *args, **kwargs)
        else:
            messages.add_message(request, messages.WARNING, "You have not submitted an application to this club!")
            return redirect(f'/club/{club_name}/apply/')

    return modified_view_function


def club_exists(view_function):
    """check whether the club exists"""

    def modified_view_function(request, club_name, *args, **kwargs):
        if Club.objects.filter(club_name=club_name).count() == 1:
            return view_function(request, club_name, *args, **kwargs)
        else:
            messages.add_message(request, messages.WARNING, "No club found with this name.")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    return modified_view_function


def club_and_book_exists(view_function):
    """check whether the club and book exists"""

    def modified_view_function(request, club_name, book_isbn, *args, **kwargs):
        if Club.objects.filter(club_name=club_name).count() == 1:
            if Book.objects.filter(ISBN=book_isbn).count() == 1:
                return view_function(request, club_name, book_isbn, *args, **kwargs)
            else:
                messages.add_message(request, messages.WARNING, "No book found with this ISBN.")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            messages.add_message(request, messages.WARNING, "No club found with this name.")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    return modified_view_function


def club_and_meeting_exists(view_function):
    """check whether the club and meeting exists"""

    def modified_view_function(request, club_name, meeting_id, *args, **kwargs):
        if Club.objects.filter(club_name=club_name).count() == 1:
            if Meeting.objects.filter(id=meeting_id).count() == 1:
                return view_function(request, club_name, meeting_id, *args, **kwargs)
            else:
                messages.add_message(request, messages.WARNING, "No meeting found with this ID.")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            messages.add_message(request, messages.WARNING, "No club found with this name.")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    return modified_view_function



def not_last_host(view_function):
    def modified_view_function(request, club_name, *args, **kwargs):
        current_club = Club.objects.get(club_name=club_name)
        current_date = datetime.now().date()
        if Meeting.objects.filter(club=current_club).count() > 0:
            latest_meeting_id = Meeting.objects.filter(club=current_club).latest('id').id
            latest_meeting = Meeting.objects.get(id=latest_meeting_id)
            if MeetingAttendance.objects.filter(meeting=latest_meeting, user=request.user,
                                                meeting_role='H').count() == 1 and current_date < latest_meeting.date:
                messages.add_message(request, messages.WARNING, "You were the last person to create a meeting. Please "
                                                                "wait until this meeting has passed or another person "
                                                                "creates a meeting.")
                return redirect('meeting_list', club_name)
            else:
                return view_function(request, club_name, *args, **kwargs)
        else:
            return view_function(request, club_name, *args, **kwargs)

    return modified_view_function

def book_exists(view_function):
    """check whether the book exists"""

    def modified_view_function(request, ISBN, *args, **kwargs):
        if Book.objects.filter(ISBN=ISBN).count() == 1:
            return view_function(request, ISBN, *args, **kwargs)
        else:
            messages.add_message(request, messages.WARNING, "No Book found with this name.")
            return redirect('book_list', 'All')

    return modified_view_function

def own_feedback_exists(view_function):
    """check whether the book_and_book_rating_review exists"""

    def modified_view_function(request, ISBN, pk, *args, **kwargs):
        if BookRatingReview.objects.filter(id=pk, user=request.user).count() == 1:
            return view_function(request, ISBN, pk, *args, **kwargs)
        elif BookRatingReview.objects.filter(id=pk).count() == 1:
            messages.add_message(request, messages.WARNING, "You have not create this feedback for this book.")
            return redirect('show_book', ISBN)
        else:
            messages.add_message(request, messages.WARNING, "No feedback with this book found with this ID.")
            return redirect('show_book', ISBN)

    return modified_view_function

def bookStatus_does_not_exists(view_function):
    """check whether the book status exists"""

    def modified_view_function(request, ISBN, *args, **kwargs):
        book = Book.objects.get(ISBN=ISBN)
        if BookStatus.objects.filter(book=book, user=request.user).count() != 0:
            messages.add_message(request, messages.WARNING, "The Book has already been added in your reading list!")
            return redirect('show_book', ISBN)
        else:
            return view_function(request, ISBN, *args, **kwargs)

    return modified_view_function

def bookStatus_exists(view_function):
    """check whether the book status exists"""

    def modified_view_function(request, ISBN, *args, **kwargs):
        book = Book.objects.get(ISBN=ISBN)
        if BookStatus.objects.filter(book=book, user=request.user).count() == 0:
            messages.add_message(request, messages.WARNING, "The Book is not in your reading list!")
            return redirect('show_book', ISBN)
        else:
            return view_function(request, ISBN, *args, **kwargs)


    return modified_view_function

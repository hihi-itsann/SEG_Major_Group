from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from .models import Club, Role, Application, Book, Meeting


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
        if Role.objects.filter(user=request.user, club=current_club).count() > 0:
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


def owner_required(view_function):
    """check whether the user is the owner"""

    def modified_view_function(request, club_name, *args, **kwargs):
        current_club = Club.objects.get(club_name=club_name)
        if Role.objects.filter(user=request.user, club=current_club).count() > 0:
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
        if Role.objects.filter(user=request.user, club=current_club).count() > 0:
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
        if Role.objects.filter(user=request.user, club=current_club).count() > 0:
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
        if Application.objects.filter(user=request.user, club=current_club).count() > 0:
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
        if Role.objects.filter(user=request.user, club=current_club).count() > 0:
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
        if Application.objects.filter(user=request.user, club=current_club).count() > 0:
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
        try:
            club = Club.objects.get(club_name=club_name)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, club_name, *args, **kwargs)

    return modified_view_function


def club_and_book_exists(view_function):
    """check whether the club and book exists"""

    def modified_view_function(request, club_name, book_isbn, *args, **kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.WARNING, "No club found with this name.")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            try:
                book = Book.objects.get(ISBN=book_isbn)
            except ObjectDoesNotExist:
                messages.add_message(request, messages.WARNING, "No book found with this ISBN.")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                return view_function(request, club_name, book_isbn, *args, **kwargs)

    return modified_view_function


def club_and_meeting_exists(view_function):
    """check whether the club and book exists"""

    def modified_view_function(request, club_name, meeting_id, *args, **kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.WARNING, "No club found with this name.")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            try:
                meeting = Meeting.objects.get(id=meeting_id)
            except ObjectDoesNotExist:
                messages.add_message(request, messages.WARNING, "No meeting found with this ID.")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                return view_function(request, club_name, meeting_id, *args, **kwargs)

    return modified_view_function

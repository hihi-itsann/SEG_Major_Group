from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from .models import User, Club, Role, Application, Book


def login_prohibited(view_function):
    """check that the user is logged in"""

    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)

    return modified_view_function


def management_required(view_function):
    """check whether the user is an officer or an owner"""

    def modified_view_function(request, club_name, *args, **kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
            role = request.user.role_set.get(club=club)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            if role.club_role == 'OFF' or role.club_role == 'OWN':
                return view_function(request, club_name, *args, **kwargs)
            else:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    return modified_view_function


def owner_required(view_function):
    """check whether the user is an owner"""

    def modified_view_function(request, club_name, *args, **kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
            role = request.user.role_set.get(club=club)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            if role.club_role == 'OWN':
                return view_function(request, club_name, *args, **kwargs)
            else:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    return modified_view_function


def membership_required(view_function):
    """check whether the user is a member"""

    def modified_view_function(request, club_name, *args, **kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
            role = request.user.role_set.get(club=club)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            if role.club_role == 'MEM' or role.club_role == 'OFF' or role.club_role == 'OWN':
                return view_function(request, club_name, *args, **kwargs)
            else:
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
                messages.add_message(request, messages.ERROR, "You have been banned from this club!")
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
                messages.add_message(request, messages.ERROR, "You have been banned from this club!")
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

from django.shortcuts import redirect
from django.conf import settings
from .models import User, Club, Role
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages


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
    """check to make sure user is not a membe or an applicant"""
    def modified_view_function(request, club_name, *args, **kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
            role = request.user.role_set.get(club=club)
        except ObjectDoesNotExist:
            return view_function(request, club_name, *args, **kwargs)
        else:
            if role.club_role == 'APP':
                messages.add_message(request, messages.WARNING, "You have already applied for this club.")
            else:
                messages.add_message(request, messages.WARNING, "You are already a member!")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    return modified_view_function


def applicant_required(view_function):
    """check to make sure user an applicant"""
    def modified_view_function(request, club_name, *args, **kwargs):
        try:
            club = Club.objects.get(club_name=club_name)
            role = request.user.role_set.get(club=club)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.WARNING, "You have not applied to this club.")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            if role.club_role == 'APP':
                return view_function(request, club_name, *args, **kwargs)
            else:
                messages.add_message(request, messages.WARNING, "You are already a member!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
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

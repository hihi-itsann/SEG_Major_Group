from django.shortcuts import redirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Book

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function

def book_exists(view_function):
    """check whether the book exists"""
    def modified_view_function(request, ISBN, *args, **kwargs):
        try:
            book = Book.objects.get(ISBN=ISBN)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, ISBN, *args, **kwargs)

    return modified_view_function

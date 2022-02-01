from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
#from bookclubs.helpers import login_prohibited
from django.contrib.auth.hashers import check_password
from django.urls import reverse

#@login_prohibited
def home(request):
    return render(request, 'home.html')

from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from bookclubs.helpers import login_prohibited
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from bookclubs.forms import SignUpForm, LogInForm
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
from django.urls import reverse
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import MultipleObjectMixin

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

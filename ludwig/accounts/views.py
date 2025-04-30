from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserLoginForm, UserRegistrationForm


class UserRegistrationView(CreateView):
    template_name = "accounts/register.html"
    form_class = UserRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        valid_form = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)

        return redirect('dashboard:home')

    def get_success_url(self):
        return reverse_lazy('dashboard:home')


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.request.GET.get("next", reverse_lazy("dashboard:home"))


@login_required
def logout_view(request):
    """Log out the user."""
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("accounts:login")
    return render(request, "accounts/logout.html")

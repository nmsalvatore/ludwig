from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserRegistrationForm, UserLoginForm


class UserRegistrationView(CreateView):
    template_name = "accounts/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your account has been created! You can now log in.")
        return response


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = form.cleaned_data.get("remember_me")

        if not remember_me:
            # Set session expiry to browser close
            self.request.session.set_expiry(0)
            self.request.session.modified = True

        messages.success(self.request, f"Welcome back, {self.request.POST.get("username")}!")
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.GET.get("next", reverse_lazy("home"))


@login_required
def logout_view(request):
    """Log out the user."""
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("accounts:login")
    return render(request, "accounts/logout.html")


@login_required
def profile_view(request):
    """View the user's profile."""
    return render(request, "accounts/profile.html")

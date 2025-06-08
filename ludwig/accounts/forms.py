from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """
    Define UserRegistrationForm which extends UserCreationForm, adds
    custom field labels and turns off autocomplete on form inputs.
    """

    username = forms.CharField(
        label="Username",
        max_length=30,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )

    email = forms.EmailField(
        label="Email address",
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "off"}),
    )

    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"autocomplete": "off"})
    )

    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class UserLoginForm(AuthenticationForm):
    """
    Defines custom UserLoginForm which extends AuthenticationForm, adds
    custom field labels and turns off autocomplete on form inputs.
    """

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "off"}),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "off"})
    )

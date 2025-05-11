from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Defines User model as subclass of AbstractUser with unique email
    address and display name.
    """

    display_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

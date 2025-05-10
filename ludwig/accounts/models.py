from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Defines User models by extending AbstractUser and adding
    custom fields.
    """

    display_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

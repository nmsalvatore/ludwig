from django.db import models


class TimeStampedModel(models.Model):
    """Abstract Model class including basic time stamps."""

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

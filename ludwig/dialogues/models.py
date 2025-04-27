from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.db import models

from ludwig.core.models import TimeStampedModel
from ludwig.accounts.models import User


class Dialogue(TimeStampedModel):
    """A model representing a conversation between multiple users."""
    is_open = models.BooleanField()
    is_visible = models.BooleanField()
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='dialogues')
    summary = models.TextField(blank=True)
    title = models.CharField(max_length=200)
    views = models.IntegerField(default=0)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return self.title


class Post(TimeStampedModel):
    """A model representing a single post within a conversation."""
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    dialogue = models.ForeignKey(Dialogue, on_delete=models.CASCADE, related_name='posts')

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return self.body[:50]

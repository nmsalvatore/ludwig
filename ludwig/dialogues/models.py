from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from nanoid import generate as generate_nanoid

from ludwig.accounts.models import User
from ludwig.base.models import TimeStampedModel


def generate_unique_id():
    return generate_nanoid(size=10)


class Dialogue(TimeStampedModel):
    id = models.CharField(
        primary_key=True,
        default=generate_unique_id,
        editable=False,
        max_length=10
    )
    is_open = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='dialogues')
    summary = models.TextField(blank=True)
    title = models.CharField(max_length=200)
    views = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return self.title


class Post(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    dialogue = models.ForeignKey(Dialogue, on_delete=models.CASCADE, related_name='posts')

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return self.body[:50]

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from .views import home_view

urlpatterns = [
    path("", home_view, name="home"),
    path("auth/", include("ludwig.accounts.urls")),
    path("dashboard/", include("ludwig.dashboard.urls")),
    path("dialogues/", include("ludwig.dialogues.urls")),
]

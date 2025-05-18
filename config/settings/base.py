import json
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from environs import Env

# load environment variables
env = Env()
env.read_env()

# set BASE_DIR to project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# set secret key
SECRET_KEY = env.str("SECRET_KEY")

# project apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ludwig.base",
    "ludwig.accounts",
    "ludwig.dashboard",
    "ludwig.dialogues",
]

# project middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# root url path
ROOT_URLCONF = "config.urls"

# template settings
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# wsgi application path
WSGI_APPLICATION = "config.wsgi.application"

# password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Los_Angeles"
USE_I18N = True
USE_TZ = True

# static files
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_URL = "staticfiles/"
STATIC_ROOT = BASE_DIR / "static_root"

# uploaded files
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media_root"

# default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# users
AUTH_USER_MODEL = "accounts.User"

# login urls
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:home"

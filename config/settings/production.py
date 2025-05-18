from environs import Env

from .base import *

env = Env()
env.read_env()

DEBUG = env.bool("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# use whitenoise for static files
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# database configuration
DATABASES = {
    "default": {
        "ENGINE": env.str("DB_ENGINE"),
        "NAME": env.str("DB_NAME"),
        "USER": env.str("DB_USER"),
        "PASSWORD": env.str("DB_PASSWORD"),
        "HOST": env.str("DB_HOST"),
        "PORT": env.str("DB_PORT"),
    }
}

# redirect all non-HTTPS requests to HTTPS
SECURE_SSL_REDIRECT = True

# tell django to trust the X-Forwarded-Proto header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# mark cookies as secure
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# hsts settings
SECURE_HSTS_SECONDS = 360 # 1 hour
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

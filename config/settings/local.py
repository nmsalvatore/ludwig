from environs import Env

from .base import *

env = Env()
env.read_env()

DEBUG = env.str("DEBUG")

# database configuration
DATABASES = {
    "default": {
        "ENGINE": env.str("DB_ENGINE"),
        "NAME": env.str("DB_NAME"),
        "HOST": env.str("DB_HOST"),
    }
}

from .settings import *

DEBUG = True

# Local SQLite or Docker DB
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'genius_local',
        'USER': 'genius_user',
        'PASSWORD': 'genius_pass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

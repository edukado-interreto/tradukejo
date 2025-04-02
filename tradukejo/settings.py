import os
from pathlib import Path

from decouple import config, Csv
from django.contrib.messages import constants as messages

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="tradukejo@ikso.net")
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

if "emaillabs" in EMAIL_BACKEND:
    ANYMAIL = {
        "EMAILLABS_SMTP_ACCOUNT": config("EMAILLABS_SMTP_ACCOUNT"),
        "EMAILLABS_APP_KEY": config("EMAILLABS_APP_KEY"),
        "EMAILLABS_SECRET_KEY": config("EMAILLABS_SECRET_KEY"),
    }

if config("MARIADB_DATABASE", default=False):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": config("MARIADB_DATABASE", default="tradukejo"),
            "USER": config("MARIADB_USER"),
            "PASSWORD": config("MARIADB_PASSWORD"),
            # Name of the service in Docker Compose:
            "HOST": config("MARIADB_HOST", default="mariadb"),
            "PORT": config("MARIADB_PORT", default=3306, cast=int),
        }
    }

INSTALLED_APPS = [
    "traduko.apps.TradukoConfig",
    "users",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_cleanup.apps.CleanupConfig",
    "anymail",
    "crispy_forms",
    "compressor",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "tradukejo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "tradukejo.context_processor.settings_context",
            ],
        },
    },
]

WSGI_APPLICATION = "tradukejo.wsgi.application"

AUTH_USER_MODEL = "users.User"

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGES = (
    ("ca", "Català"),
    ("cs", "Česky"),
    ("en", "English"),
    ("eo", "Esperanto"),
    ("fi", "Suomi"),
    ("fr", "Français"),
    ("it", "Italiano"),
    ("ms", "Bahasa Melayu"),
    ("nl", "Nederlands"),
    ("pl", "Polski"),
    ("pt", "Português"),
    ("sk", "Slovenčina"),
)

LANGUAGE_CODE = "eo"

TIME_ZONE = "Europe/Bratislava"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")

COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)

MESSAGE_TAGS = {
    messages.ERROR: "danger",  # Compatibility with Bootstrap
}

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "projects"
LOGOUT_REDIRECT_URL = "projects"
WEBSITE_NAME = "Tradukejo de E@I"

MEDIA_URL = "/upload/"
MEDIA_ROOT = os.path.join(BASE_DIR, "upload")

CRISPY_TEMPLATE_PACK = "bootstrap4"

MAX_LOADED_STRINGS = 30

COMPRESS_OFFLINE = config("COMPRESS_OFFLINE", default=not DEBUG)
LIBSASS_OUTPUT_STYLE = config(
    "LIBSASS_OUTPUT_STYLE", default="nested" if DEBUG else "compressed"
)
# STATICFILES_STORAGE = config("STATICFILES_STORAGE", default="django.contrib.staticfiles.storage.ManifestStaticFilesStorage")
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

import os
from pathlib import Path

import pymysql
from django.contrib.messages import constants as messages
from toml_decouple import config

from .api.settings import REST_FRAMEWORK, SPECTACULAR_SETTINGS
from .error_tracking import setup_bugsink
from .utils import Environment

SECRET_KEY = config("SECRET_KEY", "NESEKURA")
DEBUG = config("DEBUG", False)
ENVIRONMENT = Environment.init(config, DEBUG)

BASE_DIR = Path(__file__).resolve().parent.parent

HOSTNAME = config("HOSTNAME", "127.0.0.1")
HOST = config("HOST", "0.0.0.0")
PORT = config("PORT", 8000)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    list({HOSTNAME, "django", "localhost", "127.0.0.1", "0.0.0.0"}),
)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS", [f"https://{h}" for h in ALLOWED_HOSTS]
)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="tradukejo@ikso.net")
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

if "emaillabs" in EMAIL_BACKEND:
    ANYMAIL = {
        "EMAILLABS_SMTP_ACCOUNT": config("EMAILLABS_SMTP_ACCOUNT", "NONE"),
        "EMAILLABS_APP_KEY": config("EMAILLABS_APP_KEY", "NONE"),
        "EMAILLABS_SECRET_KEY": config("EMAILLABS_SECRET_KEY", "NONE"),
    }
if "MARIADB_DATABASE" in config:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": config("MARIADB_DATABASE", "tradukejo"),
            "USER": config("MARIADB_USER", "ikso"),
            "PASSWORD": config("MARIADB_PASSWORD", "NONE"),
            # Name of the service in Docker Compose:
            "HOST": config("MARIADB_HOST", "mariadb"),
            "PORT": config("MARIADB_PORT", 3306),
        }
    }
    if ENVIRONMENT.testing:
        DATABASES["default"]["HOST"] = "127.0.0.1"

    # Fake PyMySQL's version and install as MySQLdb
    pymysql.install_as_MySQLdb()

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
    "django_extensions",
    "rest_framework",
    "drf_spectacular",
    "drf_standardized_errors",
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

ROOT_URLCONF = "config.urls"

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
                "config.context_processor.settings_context",
            ],
        },
    },
]

REST_FRAMEWORK = REST_FRAMEWORK
SPECTACULAR_SETTINGS = SPECTACULAR_SETTINGS

WSGI_APPLICATION = "config.wsgi.application"

AUTH_USER_MODEL = "users.User"

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGES = [
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
]

LANGUAGE_CODE = "eo"

USE_TZ = True
TIME_ZONE = "Europe/Bratislava"


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

COMPRESS_OFFLINE = config("COMPRESS_OFFLINE", ENVIRONMENT.deployed)
LIBSASS_OUTPUT_STYLE = config(
    "LIBSASS_OUTPUT_STYLE", default="nested" if DEBUG else "compressed"
)

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["console"]},
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": True},
    },
    "formatters": {
        "app": {
            "format": (
                "%(asctime)s [%(levelname)-8s] (%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}

GIT_COMMIT = config("GIT_COMMIT", "")

DEEPL_URL = "https://api-free.deepl.com/v2"

if ENVIRONMENT.deployed:
    setup_bugsink(config)

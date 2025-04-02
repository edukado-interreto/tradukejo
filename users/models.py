from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class User(AbstractUser):
    email = models.EmailField(_("settings#email"), blank=False, unique=True)
    objects = UserManager()

    email_new_texts = models.BooleanField(_("settings#email-new-texts"), default=True)
    email_translation_request = models.BooleanField(
        _("settings#email-translation-request"), default=True
    )
    email_new_comments = models.BooleanField(
        _("settings#email-new-comments"), default=True
    )

    email_language = models.CharField(
        _("settings#email-language"),
        max_length=5,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
    )

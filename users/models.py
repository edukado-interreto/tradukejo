from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


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
        max_length=8,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
    )


def deepl_api_key(value):
    error = ValidationError(_("settings#deepl_invalid_api_key"))
    try:
        uid, suffix = value.split(":")
    except ValueError:
        raise error
    if len(uid) != 36 or len(uid.split("-")) != 5:
        raise error


class DeeplAuthKey(models.Model):
    class DeeplPlans(models.TextChoices):
        FREE = "free", "Free"
        DEVELOPER = "dev", "Developer"
        GROWTH = "grow", "Growth"
        ENTERPRISE = "entr", "Entreprise"

    api_key = models.CharField(
        "API key",
        max_length=50,
        validators=[deepl_api_key],
        unique=True,
        help_text="Ekzemple: a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6:fx",
    )
    name = models.CharField(max_length=50, blank=True)
    plan = models.CharField(
        max_length=4, choices=DeeplPlans.choices, default=DeeplPlans.FREE
    )
    character_count = models.IntegerField("Character count", default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("settings#deepl_auth_key")
        verbose_name_plural = _("settings#deepl_auth_keys")

    def __str__(self):
        return f"{self.api_key[:4]}{'*' * 6}{self.api_key[-4:]}"

    @property
    def character_limit(self):
        return 500_000 if self.plan == self.DeeplPlans.FREE else 1_000_000

    @classmethod
    def get_least_used(cls):
        return cls.objects.order_by("character_count").first()

    def update_count(self, count: int):
        rows = self.__class__.objects.filter(pk=self.pk).update(character_count=count)
        if rows == 1:
            self.character_count = count  # instead of self.refresh_from_db()
            return count
        return None

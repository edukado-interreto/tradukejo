from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy


class User(AbstractUser):
    email = models.EmailField(gettext_lazy('Email'), blank=False, unique=True)
    objects = UserManager()

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy


class User(AbstractUser):
    email = models.EmailField(gettext_lazy('Email'), blank=False, unique=True)
    objects = UserManager()

    email_new_texts = models.BooleanField('Informi min retpoŝte, kiam estas novaj tekstoj por traduki',
                                          default=True)
    email_translation_request = models.BooleanField('Informi min retpoŝte, kiam iu petas rajton traduki projekton, kiun mi administras',
                                                    default=True)
    email_new_comments = models.BooleanField('Informi min retpoŝte, kiam iu respondis mian komenton',
                                             default=True)

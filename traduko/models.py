import json, re
from collections import OrderedDict
from html import unescape

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.html import linebreaks

from .cpython_gettext import c2py
from .templatetags.traduko_tags import highlight_placeholders

TRANSLATION_STATE_TRANSLATED = 1
TRANSLATION_STATE_UNTRANSLATED = 0
TRANSLATION_STATE_OUTDATED = 2
TRANSLATION_STATES = [
    (TRANSLATION_STATE_TRANSLATED, "Translated"),
    (TRANSLATION_STATE_UNTRANSLATED, "Untranslated"),
    (TRANSLATION_STATE_OUTDATED, "Outdated"),
]

ACTION_TYPE_TRANSLATE = "trans"
ACTION_TYPE_EDIT = "edit"
ACTION_TYPE_ADD = "add"
ACTION_TYPE_IMPORT = "imp"

ACTION_TYPES = [
    (ACTION_TYPE_TRANSLATE, "translated"),
    (ACTION_TYPE_EDIT, "edited"),
    (ACTION_TYPE_ADD, "added"),
    (ACTION_TYPE_IMPORT, "imported"),
]

STATE_FILTER_ALL = ""
STATE_FILTER_UNTRANSLATED = "untr"
STATE_FILTER_OUTDATED = "outd"
STATE_FILTER_OUTDATED_UNTRANSLATED = "unout"
STATE_FILTER_CHOICES = [
    STATE_FILTER_ALL,
    STATE_FILTER_UNTRANSLATED,
    STATE_FILTER_OUTDATED,
    STATE_FILTER_OUTDATED_UNTRANSLATED,
]

SORT_STRINGS_BY_NEWEST = "new"
SORT_STRINGS_BY_OLDEST = "old"
SORT_STRINGS_BY_NAME = ""


def project_image_upload_location(instance, filename):
    extension = filename.split(".")[-1]
    return "projects/%s.%s" % (instance.pk, extension)


class Language(models.Model):
    DIRECTION_LTR = "ltr"
    DIRECTION_RTL = "rtl"
    DIRECTION_CHOICES = [
        (DIRECTION_LTR, "Left to right →"),
        (DIRECTION_RTL, "Right to left ←"),
    ]

    code = models.CharField(
        primary_key=True, max_length=8, help_text="ISO 639-1 or ISO 639-2 code"
    )
    name = models.CharField(
        max_length=60, unique=True, help_text="Name in the language itself"
    )
    direction = models.CharField(
        max_length=3, choices=DIRECTION_CHOICES, default=DIRECTION_LTR
    )
    plural_forms = models.CharField(
        max_length=200,
        help_text="Plurals header in .po files. Must begin with “nplurals=n;” where n is the number of different plural forms. Do not touch if you don’t know what you’re doing.",
    )
    google = models.BooleanField(
        default=False, help_text="Is the language available in Google Translate?"
    )
    yandex = models.BooleanField(
        default=False, help_text="Is the language available in Yandex.Translate?"
    )
    deepl = models.BooleanField(
        default=False, help_text="Is the language available in DeepL?"
    )

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def to_dict(self):
        d = {
            "code": self.code,
            "name": self.name,
            "direction": self.direction,
            "google": self.google,
            "yandex": self.yandex,
            "deepl": self.deepl,
            "plural_examples_list": self.plural_examples_list(),
        }
        return d

    def nplurals(self):
        return int(
            self.plural_forms[9]
        )  # Doesn't work if there are 10 or more plural forms, but it should never happen.

    def plural_examples_list(self):
        p = re.sub(r"^.*plural=([^;]+);?$", r"\1", self.plural_forms)
        rule = c2py(p)

        examples = []

        for n in range(self.nplurals()):
            examples.append([])

        for i in range(105):  # Arabic should be the only one needing forms after 100
            result = rule(i)
            examples[result].append(str(i))

        text_examples = []
        for e in examples:
            if len(e) > 5:
                text_examples.append(", ".join(e[0:5]) + "…")
            elif int(e[-1]) > 100:
                text_examples.append(", ".join(e) + "…")
            else:
                text_examples.append(", ".join(e))
        return text_examples


class Project(models.Model):
    name = models.CharField(max_length=80, unique=True)
    url = models.URLField(blank=True)
    source_language = models.ForeignKey("Language", on_delete=models.PROTECT)
    image = models.ImageField(blank=True, upload_to=project_image_upload_location)
    description = models.TextField(blank=True)
    update_explanations = models.TextField(
        blank=True,
        help_text="Explanations for translators: how are translations updated in the website?",
    )
    export_explanations = models.TextField(
        blank=True,
        help_text="Explanations for project admins: how to export the translations?",
    )
    needed_languages = models.ManyToManyField(
        "Language",
        blank=True,
        related_name="needed_languages",
        help_text="Leave empty if all languages are needed",
    )
    strings = models.IntegerField(default=0)
    words = models.IntegerField(default=0)
    characters = models.IntegerField(default=0)
    visible = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)
    last_translator_notification = models.DateTimeField(
        blank=True, null=True, default=None
    )
    create_date = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)

    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.name


# Each translation project has language versions: languages in which the content is being translated
class LanguageVersion(models.Model):
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    language = models.ForeignKey("Language", on_delete=models.PROTECT)
    translators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    translated_strings = models.IntegerField(default=0)
    translated_words = models.IntegerField(default=0)
    translated_characters = models.IntegerField(default=0)
    outdated_strings = models.IntegerField(default=0)
    outdated_words = models.IntegerField(default=0)
    outdated_characters = models.IntegerField(default=0)

    class Meta:
        ordering = ["language"]

    def __str__(self):
        return f"{self.project.name} - {self.language.code}"

    def untranslated_strings(self):
        return self.project.strings - self.translated_strings - self.outdated_strings

    def untranslated_words(self):
        return self.project.words - self.translated_words - self.outdated_words

    def untranslated_characters(self):
        return (
            self.project.characters
            - self.translated_characters
            - self.outdated_characters
        )

    def translated_percent(self):
        return (
            0
            if self.project.words == 0
            else self.translated_words / self.project.words * 100
        )

    def outdated_percent(self):
        return (
            0
            if self.project.words == 0
            else self.outdated_words / self.project.words * 100
        )

    def untranslated_percent(self):
        return (
            0
            if self.project.words == 0
            else self.untranslated_words() / self.project.words * 100
        )


class TranslatorRequest(models.Model):
    language_version = models.ForeignKey("LanguageVersion", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    explanation = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.language_version}"


# I'd rather not call this class "String" to avoid problems
class TrString(models.Model):
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    path = models.CharField(
        max_length=200,
        blank=True,
        help_text="Path of the string, can contain slashes for subfolders",
    )
    name = models.CharField(max_length=200)
    words = models.IntegerField(default=0)
    characters = models.IntegerField(default=0)
    context = models.TextField(
        blank=True, help_text="Short explanation for translators"
    )
    last_change = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.path}#{self.name}"

    def to_dict(self, original_text=None, translated_text=None):
        d = {
            "id": self.pk,
            "name": self.name,
            "path": self.path,
            "context": self.context,
        }
        if original_text:
            d["original_text"] = original_text.to_dict()
        if translated_text:
            d["translated_text"] = translated_text.to_dict()
            d["state"] = translated_text.state
        else:
            d["translated_text"] = None
            d["state"] = TRANSLATION_STATE_UNTRANSLATED

        d["translated_languages"] = {}
        for l in self.trstringtext_set.all().order_by("language__name"):
            d["translated_languages"][l.language.code] = l.language.name
        return d

    class Meta:
        indexes = [
            models.Index(fields=["project", "path", "name"]),
        ]
        unique_together = [["project", "path", "name"]]


class TrStringText(models.Model):
    trstring = models.ForeignKey("TrString", on_delete=models.CASCADE)
    language = models.ForeignKey("Language", on_delete=models.PROTECT)
    pluralized = models.BooleanField(default=False)
    text = models.TextField(
        help_text="If not pluralized, store text directly. If pluralized, store as JSON array."
    )
    translated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    last_change = models.DateTimeField(auto_now_add=True)  # Has to be updated manually!
    state = models.IntegerField(
        choices=TRANSLATION_STATES, default=TRANSLATION_STATE_TRANSLATED
    )

    def __str__(self):
        return f"{self.trstring} ‑ {self.language.code}"

    def to_dict(self):
        d = {
            "id": self.pk,
            "language": self.language.to_dict(),
            "pluralized": self.pluralized,
            "raw_text": self.pluralized_text_dictionary(),
            "text": {},
            "last_change": date_format(self.last_change, "DATETIME_FORMAT"),
            "old_versions": self.old_versions(),
            "comments": self.comments(),
        }
        for k, v in d["raw_text"].items():
            d["text"][k] = linebreaks(highlight_placeholders(v))
        if self.translated_by:
            d["translated_by"] = {
                "id": self.translated_by.pk,
                "username": self.translated_by.username,
                "profile_url": reverse("profile", args=[self.translated_by.pk]),
            }
        return d

    def old_versions(self):
        return self.trstringtexthistory_set.count()

    def comments(self):
        return self.comment_set.count()

    def pluralized_text_dictionary(self):
        try:
            texts = json.loads(self.text)
            if (
                type(texts) != list
            ):  # json.loads can parse self.text as an int or float, which isn't what we want
                texts = [self.text]
        except ValueError as e:
            texts = [self.text]

        if self.pluralized:
            textdict = OrderedDict()
            numbers = self.language.plural_examples_list()
            for i in range(min(len(texts), len(numbers))):
                textdict[numbers[i]] = texts[i]
            return textdict
        else:
            return {"1": texts[0]}

    def number_of_pluralized_texts(
        self,
    ):  # Unlike pluralized_text_dictionary(), can return more than 1 even if the string is not pluralized
        try:
            texts = json.loads(self.text)
            if (
                type(texts) != list
            ):  # json.loads can parse self.text as an int or float, which isn't what we want
                return 1
            return len(texts)
        except ValueError as e:
            return 1

    class Meta:
        indexes = [
            models.Index(fields=["trstring", "language"]),
        ]
        unique_together = [["trstring", "language"]]


class TrStringTextHistory(models.Model):
    trstringtext = models.ForeignKey("TrStringText", on_delete=models.CASCADE)
    pluralized = models.BooleanField(default=False)
    text = models.TextField(
        help_text="If not pluralized, store text directly. If pluralized, store as JSON array."
    )
    translated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    create_date = models.DateTimeField(
        default=timezone.now
    )  # Not auto_now_add because set manually when importing

    def __str__(self):
        return self.text

    def to_dict(self, comparison):
        d = {
            "id": self.pk,
            "pluralized": self.pluralized,
            "create_date": date_format(self.create_date, "DATETIME_FORMAT"),
            "comparison": {},
        }
        for k, v in comparison.items():
            d["comparison"][k] = linebreaks(highlight_placeholders(v, escape=False))
        if self.translated_by:
            d["translated_by"] = {
                "id": self.translated_by.pk,
                "username": self.translated_by.username,
                "profile_url": reverse("profile", args=[self.translated_by.pk]),
            }
        return d

    def pluralized_text_dictionary(self):
        try:
            texts = json.loads(self.text)
            if (
                type(texts) != list
            ):  # json.loads can parse self.text as an int or float, which isn't what we want
                texts = [self.text]
        except ValueError as e:
            texts = [self.text]

        if self.pluralized:
            textdict = OrderedDict()
            numbers = self.trstringtext.language.plural_examples_list()
            for i in range(min(len(texts), len(numbers))):
                textdict[numbers[i]] = texts[i]
            return textdict
        else:
            return {"1": texts[0]}


class StringActivity(models.Model):
    trstringtext = models.ForeignKey("TrStringText", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
    )
    language = models.ForeignKey("Language", on_delete=models.PROTECT)
    action = models.CharField(max_length=5, choices=ACTION_TYPES)
    words = models.IntegerField(null=True, default=None)
    characters = models.IntegerField(null=True, default=None)
    date = models.DateField(auto_now_add=True)
    datetime = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    trstringtext = models.ForeignKey("TrStringText", on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    text = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)

    def date(self):
        return self.create_date.date()

    def to_dict(self):
        d = {
            "id": self.pk,
            "text": self.text,
            "create_date": date_format(self.create_date, "DATETIME_FORMAT"),
        }
        if self.author:
            d["author"] = {
                "id": self.author.pk,
                "username": self.author.username,
                "profile_url": reverse("profile", args=[self.author.pk]),
            }
        return d

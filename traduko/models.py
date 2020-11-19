import json
from collections import OrderedDict
from django.db import models
from django.conf import settings

TRANSLATION_STATE_TRANSLATED = 1
TRANSLATION_STATE_UNTRANSLATED = 0
TRANSLATION_STATE_OUTDATED = 2
TRANSLATION_STATES = [
    (TRANSLATION_STATE_TRANSLATED, 'Translated'),
    (TRANSLATION_STATE_UNTRANSLATED, 'Untranslated'),
    (TRANSLATION_STATE_OUTDATED, 'Outdated'),
]

STATE_FILTER_ALL = ''
STATE_FILTER_UNTRANSLATED = 'untr'
STATE_FILTER_OUTDATED = 'outd'
STATE_FILTER_OUTDATED_UNTRANSLATED = 'unout'
STATE_FILTER_CHOICES = [STATE_FILTER_ALL, STATE_FILTER_UNTRANSLATED, STATE_FILTER_OUTDATED,
                        STATE_FILTER_OUTDATED_UNTRANSLATED]


class Language(models.Model):
    DIRECTION_LTR = 'ltr'
    DIRECTION_RTL = 'rtl'
    DIRECTION_CHOICES = [
        (DIRECTION_LTR, 'Left to right →'),
        (DIRECTION_RTL, 'Right to left ←'),
    ]

    code = models.CharField(primary_key=True,
                            max_length=6,
                            help_text="ISO 639-1 or ISO 639-2 code")
    name = models.CharField(max_length=60,
                            unique=True,
                            help_text="Name in the language itself")
    direction = models.CharField(max_length=3,
                                 choices=DIRECTION_CHOICES,
                                 default=DIRECTION_LTR)
    plural_forms = models.CharField(max_length=200,
                                    help_text="Plurals header in .po files. Must begin with “nplurals=n;” where n is the number of different plural forms. Do not touch if you don’t know what you’re doing.")
    plural_examples = models.CharField(max_length=50,
                                       blank=True,
                                       help_text="Numbers to illustrate plural rules separated by commas, e.g. for Polish: 1,2,5. Must have the same amount of numbers as nplural in the “Plural forms” field.")

    def __str__(self):
        return "{} - {}".format(self.code, self.name)

    def nplurals(self):
        return int(self.plural_forms[9])  # Doesn't work if there are 10 or more plural forms, but it should never happen.

    def plural_examples_list(self):
        examples = self.plural_examples.split(',')
        if len(examples) == self.nplurals():
            return examples
        else:
            return ["1"]


class Project(models.Model):
    name = models.CharField(max_length=80,
                            unique=True)
    url = models.URLField()
    source_language = models.ForeignKey('Language',
                                         on_delete=models.PROTECT)
    # image
    description = models.TextField(blank=True)
    needed_languages = models.ManyToManyField('Language',
                                              blank=True,
                                              related_name='needed_languages',
                                              help_text='Leave empty if all languages are needed')
    strings = models.IntegerField(default=0)
    words = models.IntegerField(default=0)
    characters = models.IntegerField(default=0)
    visible = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)

    # admins

    def __str__(self):
        return self.name


# Each translation project has language versions: languages in which the content is being translated
class LanguageVersion(models.Model):
    project = models.ForeignKey('Project',
                                on_delete=models.CASCADE)
    language = models.ForeignKey('Language',
                                 on_delete=models.PROTECT)
    translators = models.ManyToManyField(settings.AUTH_USER_MODEL)
    translator_requests = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                                 related_name="translator_requests")  # Request dates?

    class Meta:
        ordering = ['language']

    def __str__(self):
        return self.project.name + " - " + self.language.code


# I'd rather not call this class "String" to avoid problems
class TrString(models.Model):
    project = models.ForeignKey('Project',
                                on_delete=models.CASCADE)
    path = models.CharField(max_length=200,
                            blank=True,
                            help_text="Path of the string, can contain slashes for subfolders")
    name = models.CharField(max_length=200)
    pluralized = models.BooleanField(default=False)
    words = models.IntegerField(default=0)
    characters = models.IntegerField(default=0)
    context = models.TextField(blank=True,
                               help_text="Short explanation for translators")

    def __str__(self):
        return self.path + "#" + self.name


class TrStringText(models.Model):
    trstring = models.ForeignKey('TrString',
                                 on_delete=models.CASCADE)
    language = models.ForeignKey('Language',
                                 on_delete=models.PROTECT)
    pluralized = models.BooleanField(default=False)
    text = models.TextField(help_text="If not pluralized, store text directly. If pluralized, store as JSON array.")
    translated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      null=True,
                                      on_delete=models.SET_NULL)
    last_change = models.DateTimeField()  # Has to be updated manually!
    state = models.IntegerField(choices=TRANSLATION_STATES,
                                default=TRANSLATION_STATE_TRANSLATED)

    def __str__(self):
        return self.text

    def pluralized_text_dictionary(self):
        try:
            texts = json.loads(self.text)
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

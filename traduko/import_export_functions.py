import csv, io

from django.utils import timezone

from .models import *
from .translation_functions import *


class WrongFormatError(Exception):
    pass


def add_language_versions(project, languages):
    for l in languages:
        if l != project.source_language:
            try:
                lv = LanguageVersion.objects.get(project=project, language=l)
            except LanguageVersion.DoesNotExist:
                lv = LanguageVersion(project=project, language=l)
                lv.save();


# TODO take into account pluralized strings
def import_string(project, languages, string_data, update_texts, user):
    path = string_data['path'].strip('/')
    name = string_data['name'].strip()
    source_language_text = string_data[project.source_language.code].strip()

    if name == '' or source_language_text == '':
        return

    words = len(source_language_text.split())
    characters = len(source_language_text)
    context = string_data['context'].strip()

    try:
        trstring = TrString.objects.get(project=project, path=path, name=name)
        string_exists = True
    except TrString.DoesNotExist:
        trstring = TrString(project=project, path=path, name=name, words=words, characters=characters, context=context)
        string_exists = False

    excluded_fields = ['path', 'name', 'context']

    if string_exists:
        if update_texts:
            trstring.context = string_data['context'].strip()
            trstring.words = len(source_language_text.split())
    else:
        trstring.context = string_data['context'].strip()
        trstring.save()

    for l in languages:
        if l.code in string_data.keys():
            translated_text = string_data[l.code].strip()
            if translated_text == '':
                continue

            if string_exists:
                try:
                    trstringtext = TrStringText.objects.get(trstring=trstring, language=l)
                    translated_text_exists = True
                except TrString.DoesNotExist:
                    translated_text_exists = False
            else:
                translated_text_exists = False

            if not translated_text_exists:
                trstringtext = TrStringText(trstring=trstring,
                                            language=l,
                                            translated_by=user,
                                            text=translated_text
                                            )
                trstringtext.save()
            elif update_texts and trstringtext.text != translated_text:
                trstringtext.text = translated_text
                trstringtext.translated_by = user
                trstringtext.last_change = timezone.now()
                trstringtext.state = TRANSLATION_STATE_TRANSLATED
                trstringtext.save()
                # TODO push current version to history? or just overwrite?
                # TODO translation status when changing the default text


def import_from_csv(project, csv_file, update_texts, user_is_author, user):
    required_fields = ['path', 'name', 'context', project.source_language.code]
    csv_file.seek(0)
    dictreader = csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))

    language_codes = [x for x in dictreader.fieldnames if x not in required_fields and x != '']
    language_codes.append(project.source_language.code)
    languages = Language.objects.filter(code__in=language_codes)

    add_language_versions(project, languages)
    for l in languages:
        update_translators_when_translating(user, project, l)

    for row in dictreader:
        for f in required_fields:
            if f not in row.keys():
                raise WrongFormatError()
        import_string(project, languages, row, update_texts, user if user_is_author else None)

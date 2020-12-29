import csv, io
from django.db.models import Case, When
from django.db.models.signals import post_save
from django.utils import timezone
from .models import *
from .translation_functions import *
from . import signals


class WrongFormatError(Exception):
    pass


def add_language_versions(project, languages):
    for l in languages:
        if l != project.source_language:
            try:
                lv = LanguageVersion.objects.get(project=project, language=l)
            except LanguageVersion.DoesNotExist:
                lv = LanguageVersion(project=project, language=l)
                lv.save()


# TODO take into account pluralized strings
def import_string(project, languages, string_data, update_texts, user):
    path = string_data['path'].strip('/ ')
    name = string_data['name'].strip()
    source_language_text = string_data[project.source_language.code].strip()

    if name == '' or source_language_text == '':
        return

    for l in languages:
        if l.code in string_data.keys():
            translated_text = string_data[l.code].strip()
            if translated_text == '':
                continue

            add_or_update_trstringtext(project,
                                       path,
                                       name,
                                       l,
                                       translated_text,
                                       user,
                                       False,  # todo: pluralized
                                       update_texts,
                                       string_data['context'].strip(),
                                       False)


def import_from_csv(project, csv_file, update_texts, user_is_author, user):
    required_fields = ['path', 'name', 'context', project.source_language.code]
    csv_file.seek(0)
    dictreader = csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))

    language_codes = [x for x in dictreader.fieldnames if x not in required_fields and x != '']
    language_codes.append(project.source_language.code)
    languages = Language.objects.filter(code__in=language_codes).order_by(
        Case(When(code=project.source_language.code, then=0), default=1)  # The source language must be first
    )
    add_language_versions(project, languages)
    for l in languages:
        update_translators_when_translating(user, project, l)

    # Temporarily disconnect signals, otherwise importing is horribly low
    post_save.disconnect(signals.update_project_count_from_trstringtext, sender=TrStringText)
    post_save.disconnect(signals.update_project_count_from_trstring, sender=TrString)

    for row in dictreader:
        for f in required_fields:
            if f not in row.keys():
                raise WrongFormatError()
        import_string(project, languages, row, update_texts, user if user_is_author else None)

    update_project_count(project)
    update_all_language_versions_count(project)

    post_save.connect(signals.update_project_count_from_trstringtext, sender=TrStringText)
    post_save.connect(signals.update_project_count_from_trstring, sender=TrString)

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


def quick_import(project, data, languages, user):
    imported_strings = 0
    trstringtexts = []
    for row in data:
        path = row['path'].strip('/ ')
        name = row['name'].strip()
        context = row['context'].strip() if 'context' in row.keys() else ''
        pluralized = (row['pluralized'] != '0') if 'pluralized' in row.keys() else False
        source_language_text = parse_submitted_text(row[project.source_language.code].strip(),
                                                    pluralized,
                                                    project.source_language.nplurals())
        if source_language_text['characters'] == 0:
            continue
        try:
            trstring = TrString.objects.get(project=project, path=path, name=name)
        except TrString.DoesNotExist:
            pass
        else:
            continue

        imported_strings = imported_strings + 1

        trstring = TrString(project=project,
                            path=path,
                            name=name,
                            context=context,
                            words=source_language_text['words'],
                            characters=source_language_text['characters'])
        trstring.save()

        for language in languages:
            if language.code in row.keys():
                translated_text = parse_submitted_text(row[language.code].strip(),
                                                       pluralized,
                                                       language.nplurals())
                if translated_text['characters'] == 0:
                    continue
                trstringtext = TrStringText(trstring=trstring,
                                            language=language,
                                            text=translated_text['text'],
                                            pluralized=pluralized,
                                            translated_by=user)
                trstringtexts.append(trstringtext)

    TrStringText.objects.bulk_create(trstringtexts)
    return imported_strings


def import_string(project, languages, string_data, update_texts, user):
    path = string_data['path'].strip('/ ')
    name = string_data['name'].strip()
    context = string_data['context'].strip() if 'context' in string_data.keys() else ''
    pluralized = (string_data['pluralized'] != '0') if 'pluralized' in string_data.keys() else False
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
                                       pluralized,
                                       update_texts,
                                       context,
                                       False)


def import_from_csv(project, csv_file, update_texts, user_is_author, user):
    required_fields = ['path', 'name', project.source_language.code]
    csv_file.seek(0)
    dictreader = csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))

    for f in required_fields:
        if f not in dictreader.fieldnames:
            raise WrongFormatError()

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

    all_data = list(dictreader)
    if update_texts:
        imported_strings = len(all_data)
        for row in all_data:
            import_string(project, languages, row, update_texts, user if user_is_author else None)
    else:
        imported_strings = quick_import(project, all_data, languages, user if user_is_author else None)

    update_project_count(project)
    update_all_language_versions_count(project)

    post_save.connect(signals.update_project_count_from_trstringtext, sender=TrStringText)
    post_save.connect(signals.update_project_count_from_trstring, sender=TrString)

    return imported_strings


def export_to_csv(project):
    fieldnames = ['path', 'name', 'pluralized', 'context', project.source_language.code]
    csv_data = []

    trstrings = project.trstring_set.all().order_by('path', 'name')
    languageversions = project.languageversion_set.all().order_by('language__code')
    trstringtexts = TrStringText.objects.filter(trstring__project=project)

    translation_data = {}
    for translation in trstringtexts:
        if translation.trstring.pk not in translation_data.keys():
            translation_data[translation.trstring.pk] = {}
        translation_data[translation.trstring.pk][translation.language.code] = translation

    for lv in languageversions:
        fieldnames.append(lv.language.code)

    for s in trstrings:
        if s.pk not in translation_data.keys() or project.source_language.code not in translation_data[s.pk].keys():
            continue
        string_data = {
            'path': s.path,
            'name': s.name,
            'context': s.context,
            'pluralized': '1' if translation_data[s.pk][project.source_language.code].pluralized else '0',
            project.source_language.code: translation_data[s.pk][project.source_language.code].text,
        }
        for lv in languageversions:
            if lv.language.code in translation_data[s.pk].keys():
                string_data[lv.language.code] = translation_data[s.pk][lv.language.code].text
        csv_data.append(string_data)

    return {
        'fieldnames': fieldnames,
        'csv_data': csv_data,
    }

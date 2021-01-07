import csv, io

from django.contrib.auth import get_user_model
from django.db.models import Case, When, Q
from django.db.models.signals import post_save
from django.utils import timezone
from .models import *
from .translation_functions import *
from . import signals


class WrongFormatError(Exception):
    pass


def get_all_languages_dictionary():
    dictionary = {}
    languages = Language.objects.all()
    for l in languages:
        dictionary[l.code] = l
    return dictionary


def get_all_users_dictionary():
    User = get_user_model()
    dictionary = {}
    users = User.objects.all()
    for u in users:
        dictionary[u.username] = u
    return dictionary


def add_language_versions(project, languages):
    for l in languages:
        if l != project.source_language:
            try:
                lv = LanguageVersion.objects.get(project=project, language=l)
            except LanguageVersion.DoesNotExist:
                lv = LanguageVersion(project=project, language=l)
                lv.save()


def quick_import(project, data, user, fallback_author=None):
    imported_strings = 0
    imported_translations = 0

    # Get max ID of current TrStrings so we can identify newly added ones later
    max_id = TrString.objects.filter(project=4).aggregate(Max('pk'))
    max_id = max_id['pk__max']
    if max_id is None:
        max_id = 0

    trstrings = TrString.objects.filter(project=project)
    all_strings = {}  # Building a dictionary with all trstrings in the current project so we can search for them easily
    for string in trstrings:
        if string.path not in all_strings.keys():
            all_strings[string.path] = {}
        if string.name not in all_strings[string.path].keys():
            all_strings[string.path][string.name] = {
                'trstring': string,
                'translations': []
            }
        for t in string.trstringtext_set.all():
            all_strings[string.path][string.name]['translations'].append(t.language.code)

    # First: create the trstrings that don't exist and add them to all_strings
    strings_to_add = []
    for string in data:
        if string['path'] not in all_strings.keys() or string['name'] not in all_strings[string['path']].keys():
            # Only if there is a translation in the source language
            if project.source_language.code in string['translations'].keys():
                source_language_text = parse_submitted_text(
                    string['translations'][project.source_language.code]['text'].strip(),
                    string['pluralized'] if 'pluralized' in string.keys() else False,
                    project.source_language.nplurals())
                trstring = TrString(project=project,
                                    path=string['path'],
                                    name=string['name'],
                                    words=source_language_text['words'],
                                    characters=source_language_text['characters'])
                if 'context' in string.keys():
                    trstring.context = string['context']
                strings_to_add.append(trstring)
    TrString.objects.bulk_create(strings_to_add)

    # Now we query the newly added strings and add them to all_strings dictionary
    new_strings = TrString.objects.filter(project=project, pk__gt=max_id)
    for string in new_strings:
        if string.path not in all_strings.keys():
            all_strings[string.path] = {}
        all_strings[string.path][string.name] = {
            'trstring': string,
            'translations': []
        }

    # Get max ID of current TrStrings so we can identify newly added ones later
    max_translation_id = TrStringText.objects.filter(trstring__project=4).aggregate(Max('pk'))
    max_translation_id = max_translation_id['pk__max']
    if max_translation_id is None:
        max_translation_id = 0

    trstringtexts_to_add = []
    all_languages = get_all_languages_dictionary()
    all_users = get_all_users_dictionary()
    # Now loop through all translations in data list and add them if they don't exist
    for string in data:
        for language_code, translation in string['translations'].items():
            if language_code not in all_strings[string['path']][string['name']]['translations']:
                language = all_languages[language_code]
                pluralized = string['pluralized'] if 'pluralized' in string.keys() else False
                parsed_text = parse_submitted_text(translation['text'].strip(),
                                                   pluralized,
                                                   language.nplurals())
                if parsed_text['characters'] > 0:
                    state = translation['state'] if 'state' in translation.keys() else TRANSLATION_STATE_TRANSLATED
                    trstringtext = TrStringText(trstring=all_strings[string['path']][string['name']]['trstring'],
                                                language=language,
                                                pluralized=pluralized,
                                                text=parsed_text['text'],
                                                state=state)

                    if 'translated_by' in translation.keys() and translation['translated_by'] in all_users:
                        trstringtext.translated_by = all_users[translation['translated_by']]
                    else:
                        trstringtext.translated_by = fallback_author

                    trstringtexts_to_add.append(trstringtext)

                    if language == project.source_language:
                        imported_strings = imported_strings + 1
                    else:
                        imported_translations = imported_translations + 1
    TrStringText.objects.bulk_create(trstringtexts_to_add)

    # Get added TrStringTexts and loop through them to add StringActivity
    activities_to_add = []
    new_trstringtexts = TrStringText.objects.filter(trstring__project=project, pk__gt=max_translation_id)
    for t in new_trstringtexts:
        activity = StringActivity(trstringtext=t,
                                  user=user,
                                  language=t.language,
                                  action=ACTION_TYPE_IMPORT,
                                  words=t.trstring.words,
                                  characters=t.trstring.characters)
        activities_to_add.append(activity)
    StringActivity.objects.bulk_create(activities_to_add)

    return {
        'imported_strings': imported_strings,
        'imported_translations': imported_translations,
    }


def slow_import(project, data, user, fallback_author=None):
    imported_strings = 0
    imported_translations = 0

    # Temporarily disconnect signals, otherwise importing is horribly low
    post_save.disconnect(signals.update_project_count_from_trstringtext, sender=TrStringText)
    post_save.disconnect(signals.update_project_count_from_trstring, sender=TrString)

    all_languages = get_all_languages_dictionary()
    all_users = get_all_users_dictionary()

    for string_data in data:
        path = string_data['path'].strip('/ ')
        name = string_data['name'].strip()
        context = string_data['context'].strip() if 'context' in string_data.keys() else ''
        pluralized = string_data['pluralized'] if 'pluralized' in string_data.keys() else False

        if name == '':
            continue

        for language_code, translation in string_data['translations'].items():
            translated_text = translation['text'].strip()
            if translated_text == '' or language_code not in all_languages:
                continue
            language = all_languages[language_code]
            state = translation['state'] if 'state' in translation.keys() else TRANSLATION_STATE_TRANSLATED
            if 'translated_by' in translation.keys() and translation['translated_by'] in all_users:
                author = all_users[translation['translated_by']]
            else:
                author = fallback_author

            # Can fail if the source language is not the first one in the list
            add_data = add_or_update_trstringtext(project,
                                                  path,
                                                  name,
                                                  language,
                                                  translated_text,
                                                  author,
                                                  pluralized=pluralized,
                                                  force_update=True,
                                                  context=context,
                                                  state=state,
                                                  importing_user=user)
            if add_data['trstringtext'] is not None:
                if language == project.source_language:
                    imported_strings = imported_strings + 1
                else:
                    imported_translations = imported_translations + 1

    post_save.connect(signals.update_project_count_from_trstringtext, sender=TrStringText)
    post_save.connect(signals.update_project_count_from_trstring, sender=TrString)

    return {
        'imported_strings': imported_strings,
        'imported_translations': imported_translations,
    }


def import_from_json(project, json_file, update_texts, user_is_author, user):
    json_file.seek(0)
    data = json.loads(json_file.read())

    language_codes = []
    for string in data:
        for l in string['translations'].keys():
            if l not in language_codes:
                language_codes.append(l)
    languages = Language.objects.filter(code__in=language_codes).order_by(
        Case(When(code=project.source_language.code, then=0), default=1)  # The source language must be first
    )
    add_language_versions(project, languages)
    for l in languages:
        update_translators_when_translating(user, project, l)

    if update_texts:
        import_stats = slow_import(project, data, user, user if user_is_author else None)
    else:
        import_stats = quick_import(project, data, user, user if user_is_author else None)

    update_project_count(project)
    update_all_language_versions_count(project)

    return import_stats


def import_from_csv(project, csv_file, update_texts, user_is_author, user):
    required_fields = ['path', 'name']
    csv_file.seek(0)
    dictreader = csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))

    for f in required_fields:
        if f not in dictreader.fieldnames:
            raise WrongFormatError()

    language_codes = [x for x in dictreader.fieldnames if x not in required_fields and x != '']
    languages = Language.objects.filter(code__in=language_codes).order_by(
        Case(When(code=project.source_language.code, then=0), default=1)  # The source language must be first
    )
    add_language_versions(project, languages)
    for l in languages:
        update_translators_when_translating(user, project, l)

    # Convert the CSV data to a list accepted by the import functions
    data = []
    for row in dictreader:
        name = row['name'].strip()
        if name != '':
            path = row['path'].strip(' /')
            string = {
                'path': path,
                'name': name,
            }
            if 'context' in dictreader.fieldnames and row['context'] != '':
                string['context'] = row['context'].strip()
            if 'pluralized' in dictreader.fieldnames and row['pluralized'] == '1':
                string['pluralized'] = True
            translations = {}
            for language in languages:
                if row[language.code] != '':
                    translations[language.code] = {'text': row[language.code].strip()}
            if len(translations) > 0:
                string['translations'] = translations
                data.append(string)

    if update_texts:
        import_stats = slow_import(project, data, user, user if user_is_author else None)
    else:
        import_stats = quick_import(project, data, user, user if user_is_author else None)

    update_project_count(project)
    update_all_language_versions_count(project)

    return import_stats


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


def export_to_json(project, path="", languages=[]):
    """
    :param project:
    :param path:
    :param languages: list of language codes or empty list for all languages.
    :return: list of dictionaries
    """
    trstrings = project.trstring_set.all().order_by('path', 'name')
    if path != "":
        trstrings = trstrings.filter(Q(path=path) | Q(path__startswith=path + "/"))
    data = []
    for s in trstrings:
        stringdata = {
            'path': s.path,
            'name': s.name,
            'translations': {}
        }
        if s.context != "":
            stringdata['context'] = s.context
        if len(languages) > 0:
            trstringtexts = s.trstringtext_set.filter(language__code__in=languages)
        else:
            trstringtexts = s.trstringtext_set.all()
        for t in trstringtexts:
            stringdata['translations'][t.language.code] = {
                'text': t.text,
                'state': t.state,
            }
            if t.language == project.source_language:
                stringdata['pluralized'] = t.pluralized
            elif t.pluralized and 'pluralized' not in stringdata.keys():
                stringdata['pluralized'] = True

            if t.translated_by is not None:
                stringdata['translations'][t.language.code]['translated_by'] = t.translated_by.username
        if len(stringdata['translations']) > 0:
            data.append(stringdata)
    return data

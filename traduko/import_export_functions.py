import csv, io, polib
from django.contrib.auth import get_user_model
from django.db.models import Case, When, Q
from django.db.models.signals import post_save
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

from .models import *
from .translation_functions import *
from . import signals
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
import demjson


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


def get_languages_for_export(project):
    languages = [
        (project.source_language.code, f'{project.source_language.code} - {project.source_language.name}')
    ]
    languageversions = project.languageversion_set.all().order_by('language__code')
    for lv in languageversions:
        languages.append((lv.language.code, f'{lv.language.code} - {lv.language.name}'))
    return languages


def add_language_versions(project, languages):
    for l in languages:
        if l != project.source_language:
            try:
                lv = LanguageVersion.objects.get(project=project, language=l)
            except LanguageVersion.DoesNotExist:
                lv = LanguageVersion(project=project, language=l)
                lv.save()


def remove_path_start(path, path_start, remove_path):
    if not remove_path or path_start == "":
        new_path = path
    elif remove_path:
        if path == path_start:
            new_path = ""
        elif path.startswith(path_start + "/"):
            new_path = path[(len(path_start) + 1):]
        else:
            new_path = path
    return new_path


def recursive_dictionary_parse(dictionary, path='', merged_dictionary={}):
    """
    Transforms a dictionary like this:
    {
        "directory": {
            "subdirectory": {
                "string": "value",
                "string2": "value",
            }
        }
    }
    Into a dictionary like this:
    {
        "directory/subdirectory": {
            "string": "value",
            "string2": "value",
        }
    }
    """
    for key, value in dictionary.items():
        if isinstance(value, dict):
            if path == '':
                new_path = key
            else:
                new_path = f'{path}/{key}'
            merged_dictionary = recursive_dictionary_parse(value, new_path)
        else:
            if path not in merged_dictionary.keys():
                merged_dictionary[path] = {}
            merged_dictionary[path][key] = value
    return merged_dictionary


def quick_import(project, data, user, fallback_author=None):
    imported_strings = 0
    imported_translations = 0

    # Get max ID of current TrStrings so we can identify newly added ones later
    max_id = TrString.objects.filter(project=project).aggregate(Max('pk'))
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
    max_translation_id = TrStringText.objects.filter(trstring__project=project).aggregate(Max('pk'))
    max_translation_id = max_translation_id['pk__max']
    if max_translation_id is None:
        max_translation_id = 0

    trstringtexts_to_add = []
    all_languages = get_all_languages_dictionary()
    all_users = get_all_users_dictionary()

    # Now loop through all translations in data list and add them if they don't exist
    for string in data:
        for language_code, translation in string['translations'].items():
            if string['path'] not in all_strings.keys() or string['name'] not in all_strings[string['path']].keys():  # Trying to import translation of non-existent string
                continue
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


def import_from_json(project, json_file, update_texts, user_is_author, user, import_to=''):
    json_file.seek(0)
    try:
        data = json.loads(json_file.read())
    except ValueError:
        raise WrongFormatError()

    language_codes = []
    import_to = import_to.strip('/ ')
    for string in data:
        if import_to != '':  # Add import path
            if string['path'] == '':
                string['path'] = import_to
            else:
                string['path'] = f'{import_to}/{string["path"]}'
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


def import_history_from_json(project, json_file):
    json_file.seek(0)
    try:
        data = json.loads(json_file.read())
    except ValueError:
        raise WrongFormatError()

    all_users = get_all_users_dictionary()

    imported = 0
    history_to_add = []
    for string in data:
        try:  # Check if the translated string exists
            trstringtext = TrStringText.objects.get(trstring__project=project,
                                                    trstring__path=string['path'],
                                                    trstring__name=string['name'],
                                                    language=string['language']
                                                    )
        except TrStringText.DoesNotExist:
            continue

        # Check if the old string already exists
        stringtime = make_aware(parse_datetime(string['datetime']))
        history = TrStringTextHistory.objects.filter(trstringtext=trstringtext, create_date=stringtime).count()
        if history > 0:
            continue

        print(trstringtext)
        stringtime = make_aware(parse_datetime(string['datetime']))
        new_history = TrStringTextHistory(trstringtext=trstringtext,
                                          create_date=str(stringtime),
                                          text=string['text'])

        if string['translated_by'] in list(all_users.keys()):
            new_history.translated_by = all_users[string['translated_by']]

        history_to_add.append(new_history)
        imported += 1

    TrStringTextHistory.objects.bulk_create(history_to_add)
    return imported


def import_from_csv(project, csv_file, update_texts, user_is_author, user, import_to=''):
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
            if import_to != '':  # Add import path
                if path == '':
                    path = import_to
                else:
                    path = f'{import_to}/{path}'
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


def import_from_po(project, po_file, update_texts, user_is_author, user, import_to=''):
    po = polib.pofile(po_file.read().decode())

    language = po.metadata['Language']

    language_codes = [language]
    languages = Language.objects.filter(code__in=language_codes)
    add_language_versions(project, languages)
    for l in languages:
        update_translators_when_translating(user, project, l)

    data = []

    for msg in po:
        if len(msg.msgstr_plural) == 0:
            if msg.msgstr == '':  # Empty translation
                continue
            text = msg.msgstr
        else:  # Plural string
            if msg.msgstr_plural[0] == '':  # Empty translation
                continue
            text = json.dumps(list(msg.msgstr_plural.values()), ensure_ascii=False)

        path_name = msg.msgid.split('#', 1)  # msgid is something like "path#name"
        if len(path_name) == 1:
            path = ''
            name = msg.msgid
        else:
            path = path_name[0]
            name = path_name[1]

        if import_to != '':  # Add import path
            if path == '':
                path = import_to
            else:
                path = f'{import_to}/{path}'

        string_data = {
            'path': path,
            'name': name,
            'pluralized': msg.msgid_plural != '',
            'translations': {
                language: {
                    'state': TRANSLATION_STATE_OUTDATED if msg.fuzzy else TRANSLATION_STATE_TRANSLATED,
                    'text': text,
                }
            }
        }
        if msg.comment != '':
            string_data['context'] = msg.comment
        data.append(string_data)

    if update_texts:
        import_stats = slow_import(project, data, user, user if user_is_author else None)
    else:
        import_stats = quick_import(project, data, user, user if user_is_author else None)

    update_project_count(project)
    update_all_language_versions_count(project)

    return import_stats


def import_from_nested_json(project, json_file, language_code, update_texts, user_is_author, user, import_to=''):
    json_file.seek(0)
    try:
        # The file could be improper JSON (e.g. no double quotes around keys), demjson accepts this but json doesn't
        json_data = demjson.decode(json_file.read())
    except demjson.JSONDecodeError as e:
        print(e)
        raise WrongFormatError()

    language = Language.objects.get(code=language_code)
    add_language_versions(project, [language])
    update_translators_when_translating(user, project, language)

    strings_to_import = recursive_dictionary_parse(json_data)

    data = []  # The list of dictionaries that will be imported

    for path, strings in strings_to_import.items():
        if import_to != '':  # Add import path
            if path == '':
                path = import_to
            else:
                path = f'{import_to}/{path}'
        for name, text in strings.items():
            # Pluralized strings are stored like this: "singular | plural ( | more forms)"
            pluralized = language.nplurals() > 1 and text.count(' | ') == (language.nplurals() - 1)
            if pluralized:
                text = json.dumps(text.split(' | '), ensure_ascii=False)

            string_data = {
                'path': path,
                'name': name,
                'pluralized': pluralized,
                'translations': {
                    language.code: {
                        'state': TRANSLATION_STATE_TRANSLATED,
                        'text': text,
                    }
                }
            }
            data.append(string_data)

    if update_texts:
        import_stats = slow_import(project, data, user, user if user_is_author else None)
    else:
        import_stats = quick_import(project, data, user, user if user_is_author else None)

    update_project_count(project)
    update_all_language_versions_count(project)

    return import_stats


def export_to_csv(project, path="", languages=[], remove_path=False):
    fieldnames = ['path', 'name', 'pluralized', 'context']
    export_source_language = project.source_language.code in languages or len(languages) == 0
    if export_source_language:
        fieldnames.append(project.source_language.code)
    csv_data = []

    trstrings = project.trstring_set.all().order_by('path', 'name')
    if path != "":
        trstrings = trstrings.filter(Q(path=path) | Q(path__startswith=path + "/"))

    if len(languages) > 0:
        if project.source_language.code not in languages:  # If not exporting source language: getting it anyway because it is necessary for data
            languages.append(project.source_language.code)
        languageversions = project.languageversion_set.filter(language__in=languages).order_by('language__code')
        trstringtexts = TrStringText.objects.filter(trstring__in=trstrings, language__in=languages)
    else:  # No language specified = all languages
        languageversions = project.languageversion_set.order_by('language__code')
        trstringtexts = TrStringText.objects.filter(trstring__in=trstrings)

    translation_data = {}
    for translation in trstringtexts:
        if translation.trstring.pk not in translation_data.keys():
            translation_data[translation.trstring.pk] = {}
        translation_data[translation.trstring.pk][translation.language.code] = translation

    for lv in languageversions:
        fieldnames.append(lv.language.code)

    for s in trstrings:
        if s.pk not in translation_data.keys() or not export_source_language and len(translation_data[s.pk]) == 1:
            continue
        new_path = remove_path_start(s.path, path, remove_path)
        string_data = {
            'path': new_path,
            'name': s.name,
            'context': s.context,
            'pluralized': '1' if translation_data[s.pk][project.source_language.code].pluralized else '0'
        }
        if export_source_language:
            string_data[project.source_language.code] = translation_data[s.pk][project.source_language.code].text
        for lv in languageversions:
            if lv.language.code in translation_data[s.pk].keys():
                string_data[lv.language.code] = translation_data[s.pk][lv.language.code].text
        csv_data.append(string_data)

    return {
        'fieldnames': fieldnames,
        'csv_data': csv_data,
    }


def export_to_json(project, path="", languages=[], remove_path=False):
    """
    :param project:
    :param path:
    :param languages: list of language codes or empty list for all languages.
    :param remove_path: if True and path is e.g. "users", then paths like "users/profile" will be changed to "profile"
    :return: list of dictionaries
    """
    trstrings = project.trstring_set.all().order_by('path', 'name')
    if path != "":
        trstrings = trstrings.filter(Q(path=path) | Q(path__startswith=path + "/"))
    data = []
    for s in trstrings:
        new_path = remove_path_start(s.path, path, remove_path)
        stringdata = {
            'path': new_path,
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


def export_to_po(response, project, **kwargs):
    """
    :param response:
    :param project:
    :param path:
    :param languages: list of language codes or empty list for all languages.
    :param remove_path: if True and path is e.g. "users", then paths like "users/profile" will be changed to "profile"
    :return: nothing, the content of the zip file is written to response
    """
    path = kwargs.get('path', '')
    remove_path = kwargs.get('remove_path', False)
    languages = kwargs.get('languages', [])
    untranslated_as_source_language = kwargs.get('untranslated_as_source_language', True)
    include_outdated = kwargs.get('include_outdated', False)
    po_file_name = kwargs.get('po_file_name', '')
    original_text_as_key = kwargs.get('original_text_as_key', '')


    trstrings = project.trstring_set.all().order_by('path', 'name')
    if path != "":
        trstrings = trstrings.filter(Q(path=path) | Q(path__startswith=path + "/"))
    for trstring in trstrings:
        trstring.original_text = TrStringText.objects.get(trstring=trstring, language=project.source_language)

    zf = ZipFile(response, 'w')

    if len(languages) == 0:
        languages = Language.objects.filter(Q(languageversion__project=project) | Q(code=project.source_language.code))
    else:
        languages = Language.objects.filter(code__in=languages)

    for language in languages:
        po = polib.POFile()
        po.metadata = {
            'Project-Id-Version': '1.0',
            'Report-Msgid-Bugs-To': settings.DEFAULT_FROM_EMAIL,
            'POT-Creation-Date': datetime.now().astimezone().strftime('%Y-%m-%d %H:%M%z'),
            'PO-Revision-Date': datetime.now().astimezone().strftime('%Y-%m-%d %H:%M%z'),
            'Last-Translator': '',
            'Language-Team': '',
            'Language': language.code,
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
            'Plural-Forms': language.plural_forms,
            'X-Generator': settings.WEBSITE_NAME,
        }
        for trstring in trstrings:
            # Getting the translation of the current string
            if language == project.source_language:
                trstringtext = trstring.original_text
            else:
                try:
                    if include_outdated:
                        trstringtext = TrStringText.objects.get(trstring=trstring, language=language)
                    else:
                        trstringtext = TrStringText.objects.get(trstring=trstring, language=language, state=TRANSLATION_STATE_TRANSLATED)
                except TrStringText.DoesNotExist:
                    if untranslated_as_source_language:
                        trstringtext = trstring.original_text
                    else:  # Blank translation
                        trstringtext = TrStringText(trstring=trstring,
                                                    language=language,
                                                    state=TRANSLATION_STATE_TRANSLATED,
                                                    pluralized=trstring.original_text.pluralized,
                                                    text='')

            entry = polib.POEntry()
            if original_text_as_key:
                if trstring.original_text.pluralized:
                    forms = list(trstring.original_text.pluralized_text_dictionary().values())
                    entry.msgid = forms[0]
                    entry.msgid_plural = forms[1] if len(forms) > 0 else forms[0]
                else:
                    entry.msgid = trstring.original_text.text
            else:
                new_path = remove_path_start(trstring.path, path, remove_path)
                entry.msgid = f'{new_path}#{trstring.name}'
                if trstring.original_text.pluralized:
                    entry.msgid_plural = f'{new_path}#{trstring.name}'

            if trstring.original_text.pluralized:
                plurals = list(trstringtext.pluralized_text_dictionary().values())
                entry.msgstr_plural = {}
                for i in range(len(plurals)):
                    entry.msgstr_plural[i] = plurals[i]
            else:
                entry.msgstr = trstringtext.text

            if trstring.context:
                entry.comment = trstring.context

            if trstringtext.state == TRANSLATION_STATE_OUTDATED:
                entry.flags.append('fuzzy')
            po.append(entry)
        # print(po.__unicode__())

        if po_file_name == '':
            filepath = language.code
        else:
            filepath = f'{language.code}/LC_MESSAGES/{po_file_name}'

        zf.writestr(f'{filepath}.po', po.__unicode__(), compress_type=ZIP_DEFLATED)
        zf.writestr(f'{filepath}.mo', po.to_binary())


def export_to_nested_json(response, project, **kwargs):
    """
    :param response:
    :param project:
    :param path:
    :param languages: list of language codes or empty list for all languages.
    :param remove_path: if True and path is e.g. "users", then paths like "users/profile" will be changed to "profile"
    :param untranslated_as_source_language: boolean
    :param include_outdated: boolean
    :param file_name: how exported files should be called
    :param export_default: add "export default" before the JSON object?
    :param export_empty: boolean
    :param export_language_name: name of key where the language name should be exported
    :param export_plural_rules: name of key where the plural rules should be exported
    :return: content of ZIP file
    """
    path = kwargs.get('path', '')
    remove_path = kwargs.get('remove_path', False)
    languages = kwargs.get('languages', [])
    untranslated_as_source_language = kwargs.get('untranslated_as_source_language', True)
    include_outdated = kwargs.get('include_outdated', False)
    file_name = kwargs.get('file_name', '{lang}.json')
    export_default = kwargs.get('export_default', False)
    export_empty = kwargs.get('export_empty', False)
    export_language_name = kwargs.get('export_language_name', '')
    export_plural_rules = kwargs.get('export_plural_rules', '')

    if '{lang}' not in file_name:
        file_name = '{lang}.json'

    trstrings = project.trstring_set.all().order_by('path', 'name')
    if path != "":
        trstrings = trstrings.filter(Q(path=path) | Q(path__startswith=path + "/"))
    for trstring in trstrings:
        trstring.original_text = TrStringText.objects.get(trstring=trstring, language=project.source_language)

    zf = ZipFile(response, 'w')

    if len(languages) == 0:
        languages = Language.objects.filter(Q(languageversion__project=project) | Q(code=project.source_language.code))
    else:
        languages = Language.objects.filter(code__in=languages)

    for language in languages:
        current_language_data = {}

        # Export language name?
        if export_language_name != '':
            language_name_path = export_language_name.split('/')
            current_key = current_language_data
            for i in range(len(language_name_path)):
                if i == len(language_name_path) - 1:
                    current_key[language_name_path[i]] = language.name
                else:
                    if language_name_path[i] not in current_key.keys():
                        current_key[language_name_path[i]] = {}
                    current_key = current_key[language_name_path[i]]

        # Export plural rules?
        if export_plural_rules != '':
            plural_rules_path = export_plural_rules.split('/')
            current_key = current_language_data
            for i in range(len(plural_rules_path)):
                if i == len(plural_rules_path) - 1:
                    current_key[plural_rules_path[i]] = language.plural_forms
                else:
                    if plural_rules_path[i] not in current_key.keys():
                        current_key[plural_rules_path[i]] = {}
                    current_key = current_key[plural_rules_path[i]]

        # Export translations
        for trstring in trstrings:
            # Getting the translation of the current string
            if language == project.source_language:
                trstringtext = trstring.original_text
            else:
                try:
                    if include_outdated:
                        trstringtext = TrStringText.objects.get(trstring=trstring, language=language)
                    else:
                        trstringtext = TrStringText.objects.get(trstring=trstring, language=language,
                                                                state=TRANSLATION_STATE_TRANSLATED)
                except TrStringText.DoesNotExist:
                    if untranslated_as_source_language:
                        trstringtext = trstring.original_text
                    else:  # Blank translation
                        trstringtext = TrStringText(trstring=trstring,
                                                    language=language,
                                                    state=TRANSLATION_STATE_TRANSLATED,
                                                    pluralized=trstring.original_text.pluralized,
                                                    text='')

            text = trstringtext.text
            if trstringtext.pluralized:
                try:
                    pluralized_text = json.loads(text)
                    text = ' | '.join(pluralized_text)
                except ValueError:
                    pass
            if text == '' and not export_empty:
                continue

            # Getting the nested path
            new_path = remove_path_start(trstring.path, path, remove_path)
            current_key = current_language_data
            if new_path != '':
                new_path = new_path.split('/')
                for p in new_path:
                    if p not in current_key.keys():
                        current_key[p] = {}
                    current_key = current_key[p]

            current_key[trstring.name] = text

        json_data = json.dumps(current_language_data, ensure_ascii=False, indent=2)
        if export_default:
            json_data = 'export default ' + json_data
        current_file_name = file_name.format(lang=language.code)
        zf.writestr(current_file_name, json_data, compress_type=ZIP_DEFLATED)

    return zf

import csv, io, polib
import hashlib

from django.contrib.auth import get_user_model
from django.db.models import Case, When
from django.db.models.signals import post_save
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from django.utils.timezone import make_aware

from .models import *
from .translation_functions import *
from . import signals
import demjson3


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
        (
            project.source_language.code,
            f"{project.source_language.code} - {project.source_language.name}",
        )
    ]
    languageversions = project.languageversion_set.all().order_by("language__code")
    for lv in languageversions:
        languages.append((lv.language.code, f"{lv.language.code} - {lv.language.name}"))
    return languages


def add_language_versions(project, languages):
    for l in languages:
        if l != project.source_language:
            try:
                lv = LanguageVersion.objects.get(project=project, language=l)
            except LanguageVersion.DoesNotExist:
                lv = LanguageVersion(project=project, language=l)
                lv.save()


# Returns a unique key for PO file import
def text_to_key(text):
    hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    slug = slugify(text)
    return slug[0:30] + hash[0:5]


def recursive_dictionary_parse(dictionary, path="", merged_dictionary={}):
    """
    Transforms a dictionary like this: {
        "directory": {
            "subdirectory": {
                "string": "value",
                "string2": "value",
            }
        }
    }
    Into a dictionary like this: {
        "directory/subdirectory": {
            "string": "value",
            "string2": "value",
        }
    }
    """
    for key, value in dictionary.items():
        if isinstance(value, dict):
            if path == "":
                new_path = key
            else:
                new_path = f"{path}/{key}"
            merged_dictionary = recursive_dictionary_parse(
                value, new_path, dict(merged_dictionary)
            )  # Python passes dictionaries as references, dict() is here to avoid strange behavior when calling the function several times in a row
        else:
            if path not in merged_dictionary.keys():
                merged_dictionary[path] = {}
            merged_dictionary[path][key] = value
    return merged_dictionary


def quick_import(project, data, user, fallback_author=None):
    imported_strings = 0
    imported_translations = 0

    # Get max ID of current TrStrings so we can identify newly added ones later
    max_id = TrString.objects.filter(project=project).aggregate(Max("pk"))
    max_id = max_id["pk__max"]
    if max_id is None:
        max_id = 0

    trstrings = TrString.objects.filter(project=project)
    all_strings = {}  # Building a dictionary with all trstrings in the current project so we can search for them easily
    for string in trstrings:
        if string.path not in all_strings.keys():
            all_strings[string.path] = {}
        if string.name not in all_strings[string.path].keys():
            all_strings[string.path][string.name] = {
                "trstring": string,
                "translations": [],
            }
        for t in string.trstringtext_set.all():
            all_strings[string.path][string.name]["translations"].append(
                t.language.code
            )

    # First: create the trstrings that don't exist and add them to all_strings
    strings_to_add = []
    for string in data:
        if (
            string["path"] not in all_strings.keys()
            or string["name"] not in all_strings[string["path"]].keys()
        ):
            # Only if there is a translation in the source language
            if project.source_language.code in string["translations"].keys():
                source_language_text = parse_submitted_text(
                    string["translations"][project.source_language.code][
                        "text"
                    ].strip(),
                    string["pluralized"] if "pluralized" in string.keys() else False,
                    project.source_language.nplurals(),
                )
                trstring = TrString(
                    project=project,
                    path=string["path"],
                    name=string["name"],
                    words=source_language_text["words"],
                    characters=source_language_text["characters"],
                )
                if "context" in string.keys():
                    trstring.context = string["context"]
                strings_to_add.append(trstring)
    TrString.objects.bulk_create(strings_to_add)

    # Now we query the newly added strings and add them to all_strings dictionary
    new_strings = TrString.objects.filter(project=project, pk__gt=max_id)
    for string in new_strings:
        if string.path not in all_strings.keys():
            all_strings[string.path] = {}
        all_strings[string.path][string.name] = {"trstring": string, "translations": []}

    # Get max ID of current TrStrings so we can identify newly added ones later
    max_translation_id = TrStringText.objects.filter(
        trstring__project=project
    ).aggregate(Max("pk"))
    max_translation_id = max_translation_id["pk__max"]
    if max_translation_id is None:
        max_translation_id = 0

    trstringtexts_to_add = []
    all_languages = get_all_languages_dictionary()
    all_users = get_all_users_dictionary()

    # Now loop through all translations in data list and add them if they don't exist
    for string in data:
        for language_code, translation in string["translations"].items():
            if (
                string["path"] not in all_strings.keys()
                or string["name"] not in all_strings[string["path"]].keys()
            ):  # Trying to import translation of non-existent string
                continue
            if (
                language_code
                not in all_strings[string["path"]][string["name"]]["translations"]
                and language_code in all_languages
            ):
                language = all_languages[language_code]
                pluralized = (
                    string["pluralized"] if "pluralized" in string.keys() else False
                )
                parsed_text = parse_submitted_text(
                    translation["text"].strip(), pluralized, language.nplurals()
                )
                if parsed_text["characters"] > 0:
                    state = (
                        translation["state"]
                        if "state" in translation.keys()
                        else TRANSLATION_STATE_TRANSLATED
                    )
                    trstringtext = TrStringText(
                        trstring=all_strings[string["path"]][string["name"]][
                            "trstring"
                        ],
                        language=language,
                        pluralized=pluralized,
                        text=parsed_text["text"],
                        state=state,
                    )

                    if (
                        "translated_by" in translation.keys()
                        and translation["translated_by"] in all_users
                    ):
                        trstringtext.translated_by = all_users[
                            translation["translated_by"]
                        ]
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
    new_trstringtexts = TrStringText.objects.filter(
        trstring__project=project, pk__gt=max_translation_id
    )
    for t in new_trstringtexts:
        activity = StringActivity(
            trstringtext=t,
            user=user,
            language=t.language,
            action=ACTION_TYPE_IMPORT,
            words=t.trstring.words,
            characters=t.trstring.characters,
        )
        activities_to_add.append(activity)
    StringActivity.objects.bulk_create(activities_to_add)

    update_project_count(project)
    update_all_language_versions_count(project)

    return {
        "imported_strings": imported_strings,
        "imported_translations": imported_translations,
    }


def slow_import(project, data, user, fallback_author=None):
    imported_strings = 0
    imported_translations = 0

    # Temporarily disconnect signals, otherwise importing is horribly slow
    post_save.disconnect(
        signals.update_project_count_from_trstringtext, sender=TrStringText
    )
    post_save.disconnect(signals.update_project_count_from_trstring, sender=TrString)

    all_languages = get_all_languages_dictionary()
    all_users = get_all_users_dictionary()

    for string_data in data:
        path = string_data["path"].strip("/ ")
        name = string_data["name"].strip()
        context = (
            string_data["context"].strip() if "context" in string_data.keys() else ""
        )
        pluralized = (
            string_data["pluralized"] if "pluralized" in string_data.keys() else False
        )

        if name == "":
            continue

        for language_code, translation in string_data["translations"].items():
            translated_text = translation["text"].strip()
            if translated_text == "" or language_code not in all_languages:
                continue
            language = all_languages[language_code]
            state = (
                translation["state"]
                if "state" in translation.keys()
                else TRANSLATION_STATE_TRANSLATED
            )
            if (
                "translated_by" in translation.keys()
                and translation["translated_by"] in all_users
            ):
                author = all_users[translation["translated_by"]]
            else:
                author = fallback_author

            # Can fail if the source language is not the first one in the list
            add_data = add_or_update_trstringtext(
                project,
                path,
                name,
                language,
                translated_text,
                author,
                pluralized=pluralized,
                force_update=True,
                context=context,
                state=state,
                importing_user=user,
            )
            if add_data["trstringtext"] is not None:
                if language == project.source_language:
                    imported_strings = imported_strings + 1
                else:
                    imported_translations = imported_translations + 1

    post_save.connect(
        signals.update_project_count_from_trstringtext, sender=TrStringText
    )
    post_save.connect(signals.update_project_count_from_trstring, sender=TrString)

    update_project_count(project)
    update_all_language_versions_count(project)

    return {
        "imported_strings": imported_strings,
        "imported_translations": imported_translations,
    }


def import_from_json(
    project, json_file, update_texts, user_is_author, user, import_to=""
):
    json_file.seek(0)
    try:
        data = json.loads(json_file.read())
    except ValueError:
        raise WrongFormatError()

    language_codes = []
    import_to = import_to.strip("/ ")
    for string in data:
        if import_to != "":  # Add import path
            if string["path"] == "":
                string["path"] = import_to
            else:
                string["path"] = f"{import_to}/{string['path']}"
        for l in string["translations"].keys():
            if l not in language_codes:
                language_codes.append(l)

    languages = Language.objects.filter(code__in=language_codes).order_by(
        Case(
            When(code=project.source_language.code, then=0), default=1
        )  # The source language must be first
    )
    add_language_versions(project, languages)
    for l in languages:
        update_translators_when_translating(user, project, l)

    if update_texts:
        import_stats = slow_import(
            project, data, user, user if user_is_author else None
        )
    else:
        import_stats = quick_import(
            project, data, user, user if user_is_author else None
        )

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
            trstringtext = TrStringText.objects.get(
                trstring__project=project,
                trstring__path=string["path"],
                trstring__name=string["name"],
                language=string["language"],
            )
        except TrStringText.DoesNotExist:
            continue

        # Check if the old string already exists
        stringtime = make_aware(parse_datetime(string["datetime"]))
        history = TrStringTextHistory.objects.filter(
            trstringtext=trstringtext, create_date=stringtime
        ).count()
        if history > 0:
            continue

        print(trstringtext)
        stringtime = make_aware(parse_datetime(string["datetime"]))
        new_history = TrStringTextHistory(
            trstringtext=trstringtext, create_date=str(stringtime), text=string["text"]
        )

        if string["translated_by"] in list(all_users.keys()):
            new_history.translated_by = all_users[string["translated_by"]]

        history_to_add.append(new_history)
        imported += 1

    TrStringTextHistory.objects.bulk_create(history_to_add)
    return imported


def import_from_csv(
    project, csv_file, update_texts, user_is_author, user, import_to=""
):
    required_fields = ["path", "name"]
    csv_file.seek(0)
    dictreader = csv.DictReader(io.StringIO(csv_file.read().decode("utf-8")))

    for f in required_fields:
        if f not in dictreader.fieldnames:
            raise WrongFormatError()

    language_codes = [
        x for x in dictreader.fieldnames if x not in required_fields and x != ""
    ]
    languages = Language.objects.filter(code__in=language_codes).order_by(
        Case(
            When(code=project.source_language.code, then=0), default=1
        )  # The source language must be first
    )
    add_language_versions(project, languages)
    for l in languages:
        update_translators_when_translating(user, project, l)

    # Convert the CSV data to a list accepted by the import functions
    data = []
    for row in dictreader:
        name = row["name"].strip()
        if name != "":
            path = row["path"].strip(" /")
            if import_to != "":  # Add import path
                if path == "":
                    path = import_to
                else:
                    path = f"{import_to}/{path}"
            string = {
                "path": path,
                "name": name,
            }
            if "context" in dictreader.fieldnames and row["context"] != "":
                string["context"] = row["context"].strip()
            if "pluralized" in dictreader.fieldnames and row["pluralized"] == "1":
                string["pluralized"] = True
            translations = {}
            for language in languages:
                if row[language.code] != "":
                    translations[language.code] = {"text": row[language.code].strip()}
            if len(translations) > 0:
                string["translations"] = translations
                data.append(string)

    if update_texts:
        import_stats = slow_import(
            project, data, user, user if user_is_author else None
        )
    else:
        import_stats = quick_import(
            project, data, user, user if user_is_author else None
        )

    return import_stats


def import_from_po(
    project,
    po_file,
    update_texts,
    user_is_author,
    user,
    import_to="",
    original_text_as_key=False,
):
    po = polib.pofile(po_file.read().decode())

    language = po.metadata["Language"]

    language_codes = [language]
    languages = Language.objects.filter(code__in=language_codes)
    add_language_versions(project, languages)
    for l in languages:
        update_translators_when_translating(user, project, l)

    data = []

    for msg in po:
        if len(msg.msgstr_plural) == 0:
            if msg.msgstr == "":  # Empty translation
                continue
            text = msg.msgstr
        else:  # Plural string
            if msg.msgstr_plural[0] == "":  # Empty translation
                continue
            text = json.dumps(list(msg.msgstr_plural.values()), ensure_ascii=False)

        if original_text_as_key:
            path = ""
            name = text_to_key(msg.msgid)
        else:
            path_name = msg.msgid.split("#", 1)  # msgid is something like "path#name"
            if len(path_name) == 1:
                path = ""
                name = msg.msgid
            else:
                path = path_name[0]
                name = path_name[1]

        if import_to != "":  # Add import path
            if path == "":
                path = import_to
            else:
                path = f"{import_to}/{path}"

        string_data = {
            "path": path,
            "name": name,
            "pluralized": msg.msgid_plural != "",
            "translations": {
                language: {
                    "state": TRANSLATION_STATE_OUTDATED
                    if msg.fuzzy
                    else TRANSLATION_STATE_TRANSLATED,
                    "text": text,
                }
            },
        }
        if msg.msgctxt != "" and msg.msgctxt is not None:
            string_data["context"] = msg.msgctxt
        elif msg.comment != "" and msg.comment is not None:
            string_data["context"] = msg.comment
        data.append(string_data)

    if update_texts:
        import_stats = slow_import(
            project, data, user, user if user_is_author else None
        )
    else:
        import_stats = quick_import(
            project, data, user, user if user_is_author else None
        )

    return import_stats


def import_from_nested_json(
    project, json_file, language_code, update_texts, user_is_author, user, import_to=""
):
    json_file.seek(0)
    file_content = json_file.read().decode("UTF-8")
    file_content = re.sub(r"^.*export default ?{", "{", file_content, flags=re.DOTALL)

    try:
        # The file could be improper JSON (e.g. no double quotes around keys), demjson accepts this but json doesn't
        json_data = demjson3.decode(file_content)
    except demjson3.JSONDecodeError as e:
        print(e)
        raise WrongFormatError()

    language = Language.objects.get(code=language_code)
    add_language_versions(project, [language])
    update_translators_when_translating(user, project, language)

    strings_to_import = recursive_dictionary_parse(json_data)

    data = []  # The list of dictionaries that will be imported

    for path, strings in strings_to_import.items():
        if import_to != "":  # Add import path
            if path == "":
                path = import_to
            else:
                path = f"{import_to}/{path}"
        for name, text in strings.items():
            # Pluralized strings are stored like this: "singular | plural ( | more forms)"
            pluralized = language.nplurals() > 1 and text.count(" | ") == (
                language.nplurals() - 1
            )
            if pluralized:
                text = json.dumps(text.split(" | "), ensure_ascii=False)

            string_data = {
                "path": path,
                "name": name,
                "pluralized": pluralized,
                "translations": {
                    language.code: {
                        "state": TRANSLATION_STATE_TRANSLATED,
                        "text": text,
                    }
                },
            }
            data.append(string_data)

    if update_texts:
        import_stats = slow_import(
            project, data, user, user if user_is_author else None
        )
    else:
        import_stats = quick_import(
            project, data, user, user if user_is_author else None
        )

    return import_stats

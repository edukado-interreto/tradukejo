import io
import json
import tarfile
from datetime import datetime
from zipfile import ZIP_DEFLATED, ZipFile

import polib
from django.conf import settings
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat

from .models import (
    TRANSLATION_STATE_OUTDATED,
    TRANSLATION_STATE_TRANSLATED,
    Language,
    TrStringText,
)

UnknownJsonData = str | dict[str, str]


def ensure_json(data: UnknownJsonData) -> str:
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False, indent=2)
    return data


def get_filtered_strings(project, strings_to_export, path):
    trstrings = project.trstring_set.all().order_by("path", "name")

    if strings_to_export != "":  # Export only the given strings
        strings_to_export = strings_to_export.split("\n")
        strings_to_export = [el.strip() for el in strings_to_export]
        trstrings = trstrings.annotate(pathname=Concat("path", V("#"), "name")).filter(
            pathname__in=strings_to_export
        )

    if path != "":  # Export only strings in path
        trstrings = trstrings.filter(Q(path=path) | Q(path__startswith=path + "/"))

    return trstrings


def remove_path_start(path, path_start, remove_path):
    if not remove_path or path_start == "":
        new_path = path
    elif remove_path:
        if path == path_start:
            new_path = ""
        elif path.startswith(path_start + "/"):
            new_path = path[(len(path_start) + 1) :]
        else:
            new_path = path
    return new_path


def export_to_csv(
    project, path="", languages=[], remove_path=False, strings_to_export=""
):
    fieldnames = ["path", "name", "pluralized", "context"]
    export_source_language = (
        project.source_language.code in languages or len(languages) == 0
    )
    if export_source_language:
        fieldnames.append(project.source_language.code)
    csv_data = []

    trstrings = get_filtered_strings(project, strings_to_export, path)

    if len(languages) > 0:
        if (
            project.source_language.code not in languages
        ):  # If not exporting source language: getting it anyway because it is necessary for data
            languages.append(project.source_language.code)
        languageversions = project.languageversion_set.filter(
            language__in=languages
        ).order_by("language__code")
        trstringtexts = TrStringText.objects.filter(
            trstring__in=trstrings, language__in=languages
        )
    else:  # No language specified = all languages
        languageversions = project.languageversion_set.order_by("language__code")
        trstringtexts = TrStringText.objects.filter(trstring__in=trstrings)

    translation_data = {}
    for translation in trstringtexts:
        if translation.trstring.pk not in translation_data.keys():
            translation_data[translation.trstring.pk] = {}
        translation_data[translation.trstring.pk][translation.language.code] = (
            translation
        )

    for lv in languageversions:
        fieldnames.append(lv.language.code)

    for s in trstrings:
        if (
            s.pk not in translation_data.keys()
            or not export_source_language
            and len(translation_data[s.pk]) == 1
        ):
            continue
        new_path = remove_path_start(s.path, path, remove_path)
        string_data = {
            "path": new_path,
            "name": s.name,
            "context": s.context,
            "pluralized": "1"
            if translation_data[s.pk][project.source_language.code].pluralized
            else "0",
        }
        if export_source_language:
            string_data[project.source_language.code] = translation_data[s.pk][
                project.source_language.code
            ].text
        for lv in languageversions:
            if lv.language.code in translation_data[s.pk].keys():
                string_data[lv.language.code] = translation_data[s.pk][
                    lv.language.code
                ].text
        csv_data.append(string_data)

    return {
        "fieldnames": fieldnames,
        "csv_data": csv_data,
    }


def export_to_json(
    project, path="", languages=[], remove_path=False, strings_to_export=""
):
    """
    :param project:
    :param path:
    :param languages: list of language codes or empty list for all languages.
    :param remove_path: if True and path is e.g. "users", then paths like "users/profile" will be changed to "profile"
    :param strings_to_export: each string (path#name) on a new line; all strings if empty
    :return: list of dictionaries
    """
    trstrings = get_filtered_strings(project, strings_to_export, path)

    data = []
    for s in trstrings:
        new_path = remove_path_start(s.path, path, remove_path)
        stringdata = {"path": new_path, "name": s.name, "translations": {}}
        if s.context != "":
            stringdata["context"] = s.context
        if len(languages) > 0:
            trstringtexts = s.trstringtext_set.filter(language__code__in=languages)
        else:
            trstringtexts = s.trstringtext_set.all()
        for t in trstringtexts:
            stringdata["translations"][t.language.code] = {
                "text": t.text,
                "state": t.state,
            }
            if t.language == project.source_language:
                stringdata["pluralized"] = t.pluralized
            elif t.pluralized and "pluralized" not in stringdata.keys():
                stringdata["pluralized"] = True

            if t.translated_by is not None:
                stringdata["translations"][t.language.code]["translated_by"] = (
                    t.translated_by.username
                )
        if len(stringdata["translations"]) > 0:
            data.append(stringdata)
    return data


def export_to_po(response, project, **kwargs):
    """
    :param response:
    :param project:
    :param path:
    :param languages: list of language codes or empty list for all languages.
    :param remove_path: if True and path is e.g. "users", then paths like "users/profile" will be changed to "profile"
    :param strings_to_export: each string (path#name) on a new line; all strings if empty
    :return: nothing, the content of the zip file is written to response
    """
    path = kwargs.get("path", "")
    remove_path = kwargs.get("remove_path", False)
    languages = kwargs.get("languages", [])
    untranslated_as_source_language = kwargs.get(
        "untranslated_as_source_language", True
    )
    include_outdated = kwargs.get("include_outdated", False)
    po_file_name = kwargs.get("po_file_name", "")
    original_text_as_key = kwargs.get("original_text_as_key", "")
    strings_to_export = kwargs.get("strings_to_export", "")

    trstrings = get_filtered_strings(project, strings_to_export, path)
    for trstring in trstrings:
        trstring.original_text = TrStringText.objects.get(
            trstring=trstring, language=project.source_language
        )

    zf = ZipFile(response, "w")

    if len(languages) == 0:
        languages = Language.objects.filter(
            Q(languageversion__project=project) | Q(code=project.source_language.code)
        )
    else:
        languages = Language.objects.filter(code__in=languages)

    for language in languages:
        po = polib.POFile()
        po.metadata = {
            "Project-Id-Version": "1.0",
            "Report-Msgid-Bugs-To": settings.DEFAULT_FROM_EMAIL,
            "POT-Creation-Date": datetime.now()
            .astimezone()
            .strftime("%Y-%m-%d %H:%M%z"),
            "PO-Revision-Date": datetime.now()
            .astimezone()
            .strftime("%Y-%m-%d %H:%M%z"),
            "Last-Translator": "",
            "Language-Team": "",
            "Language": language.code,
            "MIME-Version": "1.0",
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Transfer-Encoding": "8bit",
            "Plural-Forms": language.plural_forms,
            "X-Generator": settings.WEBSITE_NAME,
        }
        for trstring in trstrings:
            # Getting the translation of the current string
            if language == project.source_language:
                trstringtext = trstring.original_text
            else:
                try:
                    if include_outdated:
                        trstringtext = TrStringText.objects.get(
                            trstring=trstring, language=language
                        )
                    else:
                        trstringtext = TrStringText.objects.get(
                            trstring=trstring,
                            language=language,
                            state=TRANSLATION_STATE_TRANSLATED,
                        )
                except TrStringText.DoesNotExist:
                    if untranslated_as_source_language:
                        trstringtext = trstring.original_text
                    else:  # Blank translation
                        trstringtext = TrStringText(
                            trstring=trstring,
                            language=language,
                            state=TRANSLATION_STATE_TRANSLATED,
                            pluralized=trstring.original_text.pluralized,
                            text="",
                        )

            entry = polib.POEntry()
            if original_text_as_key:
                if trstring.original_text.pluralized:
                    forms = list(
                        trstring.original_text.pluralized_text_dictionary().values()
                    )
                    entry.msgid = forms[0]
                    entry.msgid_plural = forms[1] if len(forms) > 0 else forms[0]
                else:
                    entry.msgid = trstring.original_text.text
            else:
                new_path = remove_path_start(trstring.path, path, remove_path)
                entry.msgid = f"{new_path}#{trstring.name}"
                if trstring.original_text.pluralized:
                    entry.msgid_plural = f"{new_path}#{trstring.name}"

            if trstring.original_text.pluralized:
                plurals = list(trstringtext.pluralized_text_dictionary().values())
                entry.msgstr_plural = {}
                for i in range(len(plurals)):
                    entry.msgstr_plural[i] = plurals[i]
            else:
                entry.msgstr = trstringtext.text

            if trstring.context:
                entry.msgctxt = trstring.context

            if trstringtext.state == TRANSLATION_STATE_OUTDATED:
                entry.flags.append("fuzzy")
            po.append(entry)

        if po_file_name == "":
            filepath = language.code
        else:
            filepath = f"{language.code}/LC_MESSAGES/{po_file_name}"

        zf.writestr(f"{filepath}.po", po.__unicode__(), compress_type=ZIP_DEFLATED)
        zf.writestr(f"{filepath}.mo", po.to_binary())


def export_to_nested_json(project, **kwargs) -> dict[str, UnknownJsonData]:
    """
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
    :param strings_to_export: each string (path#name) on a new line; all strings if empty
    :return: content of ZIP file
    """
    path = kwargs.get("path", "")
    remove_path = kwargs.get("remove_path", False)
    languages = kwargs.get("languages", [])
    untranslated_as_source_language = kwargs.get(
        "untranslated_as_source_language", True
    )
    include_outdated = kwargs.get("include_outdated", False)
    file_name = kwargs.get("file_name", "{lang}.json")
    export_default = kwargs.get("export_default", False)
    export_empty = kwargs.get("export_empty", False)
    export_language_name = kwargs.get("export_language_name", "")
    export_plural_rules = kwargs.get("export_plural_rules", "")
    strings_to_export = kwargs.get("strings_to_export", "")

    if "{lang}" not in file_name:
        file_name = "{lang}.json"

    trstrings = get_filtered_strings(project, strings_to_export, path)
    for trstring in trstrings:
        trstring.original_text = TrStringText.objects.get(
            trstring=trstring, language=project.source_language
        )

    if languages:
        languages = Language.objects.filter(code__in=languages)
    else:
        languages = Language.objects.filter(
            Q(languageversion__project=project) | Q(code=project.source_language.code)
        )

    json_data_by_language = {}

    for language in languages:
        current_language_data = {}

        # Export language name?
        if export_language_name != "":
            language_name_path = export_language_name.split("/")
            current_key = current_language_data
            for i in range(len(language_name_path)):
                if i == len(language_name_path) - 1:
                    current_key[language_name_path[i]] = language.name
                else:
                    if language_name_path[i] not in current_key.keys():
                        current_key[language_name_path[i]] = {}
                    current_key = current_key[language_name_path[i]]

        # Export plural rules?
        if export_plural_rules != "":
            plural_rules_path = export_plural_rules.split("/")
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
                        trstringtext = TrStringText.objects.get(
                            trstring=trstring, language=language
                        )
                    else:
                        trstringtext = TrStringText.objects.get(
                            trstring=trstring,
                            language=language,
                            state=TRANSLATION_STATE_TRANSLATED,
                        )
                except TrStringText.DoesNotExist:
                    if untranslated_as_source_language:
                        trstringtext = trstring.original_text
                    else:  # Blank translation
                        trstringtext = TrStringText(
                            trstring=trstring,
                            language=language,
                            state=TRANSLATION_STATE_TRANSLATED,
                            pluralized=trstring.original_text.pluralized,
                            text="",
                        )

            text = trstringtext.text
            if trstringtext.pluralized:
                try:
                    pluralized_text = json.loads(text)
                    text = " | ".join(pluralized_text)
                except ValueError:
                    pass
            if text == "" and not export_empty:
                continue

            # Getting the nested path
            new_path = remove_path_start(trstring.path, path, remove_path)
            current_key = current_language_data
            if new_path != "":
                new_path = new_path.split("/")
                for p in new_path:
                    if p not in current_key.keys():
                        current_key[p] = {}
                    current_key = current_key[p]

            current_key[trstring.name] = text

        json_data_by_language[language.code] = current_language_data

    if export_default:
        # Note: values are not JSON anymore
        return {
            lang: f"export default {ensure_json(lang_data)}"
            for lang, lang_data in json_data_by_language.items()
        }
    return json_data_by_language


def nested_json_as_zip(
    json_data_by_language: dict[str, UnknownJsonData], lang_file_name
):
    buffer = io.BytesIO()

    with ZipFile(buffer, "w", ZIP_DEFLATED) as zf:
        for lang, json_data in json_data_by_language.items():
            zf.writestr(lang_file_name.format(lang=lang), ensure_json(json_data))

    buffer.seek(0)
    return buffer


def nested_json_as_tar_gz(
    json_data_by_language: dict[str, UnknownJsonData], lang_file_name
):
    buffer = io.BytesIO()

    with tarfile.open(fileobj=buffer, mode="w|gz") as tf:
        for lang, json_data in json_data_by_language.items():
            json_string = ensure_json(json_data)
            # Encode to bytes for writing to the tar file
            json_bytes = json_string.encode("utf-8")

            # Create TarInfo object
            file_name = lang_file_name.format(lang=lang)
            tar_info = tarfile.TarInfo(name=file_name)
            tar_info.size = len(json_bytes)
            tar_info.mtime = int(datetime.now().timestamp())

            tf.addfile(tar_info, io.BytesIO(json_bytes))

    buffer.seek(0)
    return buffer

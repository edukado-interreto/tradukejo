import json
import tarfile
from zipfile import ZipFile

import pytest

from traduko import export_functions as uut
from traduko.tests.factories import (
    LanguageVersionFactory,
    TrStringFactory,
    TrStringTextFactory,
)


@pytest.mark.django_db
def test_get_filtered_strings():
    lv = LanguageVersionFactory()
    for name in "wan tu luka".split():
        TrStringFactory(project=lv.project, name=name, path="ui")
    strings_to_export = "\n".join(["ui#tu", "ui#wan"])

    res = uut.get_filtered_strings(lv.project, strings_to_export, path="ui")
    assert set(res.values_list("name", flat=True)) == {"wan", "tu"}


def test_remove_path_start():
    REMOVE, LEAVE = True, False
    assert uut.remove_path_start("ui/main/form", "", REMOVE) == "ui/main/form"
    assert uut.remove_path_start("ui/main/form", "ui", REMOVE) == "main/form"
    assert uut.remove_path_start("ui/main/form", "ui/main", REMOVE) == "form"
    assert uut.remove_path_start("ui/main/form", "ui/main/form", REMOVE) == ""
    assert uut.remove_path_start("ui/main/form", "other", REMOVE) == "ui/main/form"
    assert uut.remove_path_start("ui/main/form", "", LEAVE) == "ui/main/form"
    assert uut.remove_path_start("ui/main/form", "ui", LEAVE) == "ui/main/form"
    assert uut.remove_path_start("ui/main/form", "ui/main", LEAVE) == "ui/main/form"


def test_gettext_file_path():
    assert uut.gettext_file_path("eo") == "eo"
    assert uut.gettext_file_path("eo", file_name="django") == "eo/LC_MESSAGES/django"


@pytest.mark.django_db
def test_export_to_csv():
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    text = TrStringTextFactory(trstring__project=lv.project, language=language)
    fieldnames = ["path", "name", "pluralized", "context", language.code]

    res = uut.export_to_csv(lv.project, languages=[language.code])
    assert res == {
        "fieldnames": fieldnames,
        "csv_data": [
            {
                "path": text.trstring.path,
                "name": text.trstring.name,
                "context": text.trstring.context,
                "pluralized": "0",
                language.code: text.text,
            }
        ],
    }

    # Export unknown language but without source language
    res = uut.export_to_csv(lv.project, languages=["xx"])
    assert res == {"fieldnames": fieldnames[:-1], "csv_data": []}

    # Specify inexistant path
    res = uut.export_to_csv(lv.project, path="xxxxx", languages=[language.code])
    assert res == {"fieldnames": fieldnames, "csv_data": []}

    TrStringTextFactory(trstring__project=lv.project, language=language)

    res = uut.export_to_csv(lv.project, path="", languages=[language.code])
    assert len(res["csv_data"]) == 2

    res = uut.export_to_csv(lv.project, path=text.trstring.path)
    assert len(res["csv_data"]) == 1


@pytest.mark.django_db
def test_export_to_json(admin_user):
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    text = TrStringTextFactory(
        trstring__project=lv.project, language=language, translated_by=admin_user
    )

    res = uut.export_to_json(lv.project)
    assert res == [
        {
            "path": text.trstring.path,
            "name": text.trstring.name,
            "translations": {
                language.code: {"text": text.text, "state": 1, "translated_by": "admin"}
            },
            "context": text.trstring.context,
            "pluralized": False,
        }
    ]
    assert res == uut.export_to_json(lv.project, languages=[language.code])


@pytest.mark.django_db
def test_export_to_po():
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    text = TrStringTextFactory(trstring__project=lv.project, language=language)

    res = uut.export_to_po(lv.project, languages=[language.code])
    pofile = res[language.code]
    assert pofile.metadata["Language"] == language.code
    poentry = pofile[0]
    assert poentry.msgctxt == text.trstring.context
    assert poentry.msgid == str(text.trstring)
    assert poentry.msgstr == text.text


@pytest.mark.django_db
def test_export_to_po_with_outdated():
    lv = LanguageVersionFactory()
    lang, source = lv.language, lv.project.source_language

    trstr = TrStringFactory(project=lv.project)
    orig = TrStringTextFactory(trstring=trstr, language=source)
    text = TrStringTextFactory(trstring=trstr, language=lang, state=2)

    res = uut.export_to_po(
        lv.project, languages=[lang.code], untranslated_as_source_language=False
    )
    poentry = res[lang.code][0]
    assert poentry.msgstr == ""
    assert not poentry.fuzzy

    res = uut.export_to_po(lv.project, languages=[lang.code])
    poentry = res[lang.code][0]
    assert poentry.msgstr == orig.text
    assert not poentry.fuzzy

    res = uut.export_to_po(lv.project, languages=[lang.code], include_outdated=True)
    poentry = res[lang.code][0]
    assert poentry.msgstr == text.text
    assert poentry.fuzzy


@pytest.mark.django_db
def test_export_to_po_pluralized():
    lv = LanguageVersionFactory()
    lang, source = lv.language, lv.project.source_language

    trstr = TrStringFactory(project=lv.project)
    TrStringTextFactory(trstring=trstr, language=source, pluralized=True)
    text = TrStringTextFactory(
        trstring=trstr, language=lang, pluralized=True, text='["wan", "tu"]'
    )

    poentry = uut.export_to_po(lv.project)[lang.code][0]
    assert poentry.msgid == str(text.trstring)
    assert poentry.msgid_plural == str(text.trstring)
    assert poentry.msgstr_plural == {0: "wan", 1: "tu"}

    text.delete()
    text = TrStringTextFactory(
        trstring=trstr, language=lang, pluralized=True, text="plain"
    )
    poentry = uut.export_to_po(lv.project)[lang.code][0]
    assert poentry.msgid == str(text.trstring)
    assert poentry.msgid_plural == str(text.trstring)
    assert poentry.msgstr_plural == {0: "plain"}


@pytest.mark.django_db
def test_po_as_zip():
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    file_path = uut.gettext_file_path(language.code, "django")
    text = TrStringTextFactory(trstring__project=lv.project, language=language)

    po_data = uut.export_to_po(lv.project, languages=[language.code])
    res = uut.po_as_zip(po_data, file_name="django")
    with ZipFile(res) as zf:
        assert zf.namelist() == [f"{file_path}.po", f"{file_path}.mo"]
        with zf.open(f"{file_path}.po") as pofile:
            content = pofile.read().decode()
            assert f'msgctxt "{text.trstring.context}"' in content
            assert f'msgid "{text.trstring}"' in content
            assert f'msgstr "{text.text}"' in content


@pytest.mark.django_db
def test_po_as_tar_gz():
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    file_path = uut.gettext_file_path(language.code, "django")
    text = TrStringTextFactory(trstring__project=lv.project, language=language)

    po_data = uut.export_to_po(lv.project, languages=[language.code])
    res = uut.po_as_tar_gz(po_data, file_name="django")

    with tarfile.open(fileobj=res, mode="r:gz") as tf:
        assert tf.getnames() == [f"{file_path}.po", f"{file_path}.mo"]

        pofile_info = tf.extractfile(f"{file_path}.po")
        assert pofile_info is not None, "PO file missing in archive"

        with pofile_info as pofile:
            content = pofile.read().decode()
            assert f'msgctxt "{text.trstring.context}"' in content
            assert f'msgid "{text.trstring}"' in content
            assert f'msgstr "{text.text}"' in content


@pytest.mark.django_db
def test_export_to_nested_json_minimal():
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    text = TrStringTextFactory(
        trstring__project=lv.project,
        trstring__path="dir",
        language=language,
    )
    res = uut.export_to_nested_json(lv.project, languages=[language.code])
    assert res == {language.code: {"dir": {text.trstring.name: text.text}}}


@pytest.mark.django_db
def test_export_to_nested_json_pluralized():
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    text = TrStringTextFactory(
        trstring__project=lv.project,
        trstring__path="",
        language=language,
        pluralized=True,
        text='["wan", "tu"]',
    )
    res = uut.export_to_nested_json(lv.project, languages=[language.code])
    assert res == {language.code: {text.trstring.name: "wan | tu"}}


@pytest.mark.django_db
def test_export_to_nested_json_with_language_name():
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    text = TrStringTextFactory(
        trstring__project=lv.project,
        trstring__path="",
        language=language,
        pluralized=True,
    )
    res = uut.export_to_nested_json(
        lv.project, languages=[language.code], export_language_name="current/lang/name"
    )
    assert res == {
        language.code: {
            text.trstring.name: text.text,
            "current": {"lang": {"name": language.name}},
        }
    }


@pytest.mark.django_db
def test_export_to_nested_json_with_plural_rules():
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    text = TrStringTextFactory(
        trstring__project=lv.project,
        trstring__path="",
        language=language,
        pluralized=True,
    )
    res = uut.export_to_nested_json(
        lv.project,
        languages=[language.code],
        export_plural_rules="current/lang/nplurals",
    )
    assert res == {
        language.code: {
            text.trstring.name: text.text,
            "current": {"lang": {"nplurals": language.plural_forms}},
        }
    }


@pytest.mark.django_db
def test_export_to_nested_json_with_export_default():
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    text = TrStringTextFactory(
        trstring__project=lv.project, trstring__path="", language=language
    )
    res = uut.export_to_nested_json(
        lv.project, languages=[language.code], export_default=True
    )
    assert res == {
        language.code: "export default {\n"
        + f'  "{text.trstring.name}": "{text.text}"'
        + "\n}"
    }


@pytest.mark.django_db
def test_nested_json_as_zip():
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    text = TrStringTextFactory(
        trstring__project=lv.project,
        trstring__path="dir",
        language=language,
    )

    po_data = uut.export_to_nested_json(lv.project, languages=[language.code])
    res = uut.nested_json_as_zip(po_data, file_name="project_{lang}.json")

    file_name = f"project_{language.code}.json"
    with ZipFile(res) as zf:
        assert zf.namelist() == [file_name]
        with zf.open(file_name) as jf:
            assert json.loads(jf.read().decode()) == {
                "dir": {text.trstring.name: text.text}
            }


@pytest.mark.django_db
def test_nested_json_as_tar_gz():
    lv = LanguageVersionFactory()
    language = lv.project.source_language
    text = TrStringTextFactory(
        trstring__project=lv.project,
        trstring__path="dir",
        language=language,
    )

    json_data = uut.export_to_nested_json(lv.project, languages=[language.code])
    res = uut.nested_json_as_tar_gz(json_data, file_name="project_{lang}.json")

    file_name = f"project_{language.code}.json"
    with tarfile.open(fileobj=res, mode="r:gz") as tf:
        assert tf.getnames() == [file_name]

        json_file = tf.extractfile(file_name)
        assert json_file is not None, "JSON file missing in archive"

        with json_file as jf:
            assert json.loads(jf.read().decode()) == {
                "dir": {text.trstring.name: text.text}
            }

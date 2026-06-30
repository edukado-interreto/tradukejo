import csv
import json
from io import BytesIO, StringIO

import polib
import pytest

from traduko import export_functions as export
from traduko import import_functions as uut
from traduko.import_functions import WrongFormatError
from traduko.models import (
    ACTION_TYPE_IMPORT,
    TRANSLATION_STATE_OUTDATED,
    LanguageVersion,
    StringActivity,
    TrString,
    TrStringText,
    TrStringTextHistory,
)
from traduko.tests.factories import (
    LanguageFactory,
    LanguageVersionFactory,
    TrStringFactory,
    TrStringTextFactory,
)


pytestmark = pytest.mark.django_db


def _json_file(data):
    return BytesIO(json.dumps(data).encode())


def _csv_file(fieldnames, rows):
    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return BytesIO(buf.getvalue().encode())


def test_text_to_key():
    key = uut.text_to_key("Hello World")
    assert key == uut.text_to_key("Hello World")
    assert key.startswith("hello-world")
    assert len(key) > len("hello-world")


def test_recursive_dictionary_parse():
    nested = {
        "directory": {
            "subdirectory": {
                "string": "value",
                "string2": "value2",
            }
        }
    }
    assert uut.recursive_dictionary_parse(nested, merged_dictionary={}) == {
        "directory/subdirectory": {
            "string": "value",
            "string2": "value2",
        }
    }
    assert uut.recursive_dictionary_parse({"hello": "world"}, merged_dictionary={}) == {
        "": {"hello": "world"}
    }


def test_get_all_languages_dictionary():
    lang = LanguageFactory()
    dictionary = uut.get_all_languages_dictionary()
    assert dictionary[lang.code] == lang


def test_get_all_users_dictionary(admin_user):
    dictionary = uut.get_all_users_dictionary()
    assert dictionary[admin_user.username] == admin_user


def test_get_languages_for_export():
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language

    res = uut.get_languages_for_export(project)
    assert res[0] == (source.code, f"{source.code} - {source.name}")
    assert (lv.language.code, f"{lv.language.code} - {lv.language.name}") in res


def test_add_language_versions():
    lv = LanguageVersionFactory()
    project = lv.project
    new_lang = LanguageFactory()

    uut.add_language_versions(project, [project.source_language, new_lang])
    assert LanguageVersion.objects.filter(project=project, language=new_lang).exists()


def test_quick_import(admin_user):
    lv = LanguageVersionFactory()
    source = lv.project.source_language
    target = lv.language

    data = [
        {
            "path": "ui",
            "name": "hello",
            "translations": {
                source.code: {"text": "Hello"},
                target.code: {"text": "Saluton", "translated_by": admin_user.username},
            },
        }
    ]
    res = uut.quick_import(lv.project, data, admin_user, fallback_author=admin_user)
    assert res == {"imported_strings": 1, "imported_translations": 1}

    trstr = TrString.objects.get(project=lv.project, path="ui", name="hello")
    assert TrStringText.objects.get(trstring=trstr, language=source).text == "Hello"
    assert TrStringText.objects.get(trstring=trstr, language=target).text == "Saluton"
    assert (
        StringActivity.objects.filter(
            trstringtext__trstring=trstr, action=ACTION_TYPE_IMPORT
        ).count()
        == 2
    )


def test_quick_import_skips_existing(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    data = [
        {
            "path": "ui",
            "name": "hello",
            "translations": {source.code: {"text": "New Hello"}},
        }
    ]
    res = uut.quick_import(project, data, admin_user)
    assert res == {"imported_strings": 0, "imported_translations": 0}
    assert TrStringText.objects.get(trstring=trstr, language=source).text == "Hello"


def test_slow_import_updates(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    data = [
        {
            "path": "ui",
            "name": "hello",
            "translations": {source.code: {"text": "New Hello"}},
        }
    ]
    res = uut.slow_import(project, data, admin_user, fallback_author=admin_user)
    assert res == {"imported_strings": 1, "imported_translations": 0}
    assert TrStringText.objects.get(trstring=trstr, language=source).text == "New Hello"


def test_import_from_json(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    target = lv.language

    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")
    TrStringTextFactory(
        trstring=trstr,
        language=target,
        text="Saluton",
        translated_by=admin_user,
    )

    exported = export.export_to_json(project)
    TrStringText.objects.filter(trstring__project=project).delete()
    TrString.objects.filter(project=project).delete()

    stats = uut.import_from_json(
        project,
        _json_file(exported),
        update_texts=False,
        user_is_author=True,
        user=admin_user,
    )
    assert stats == {"imported_strings": 1, "imported_translations": 1}

    trstr = TrString.objects.get(project=project, path="ui", name="hello")
    assert TrStringText.objects.get(trstring=trstr, language=source).text == "Hello"
    assert TrStringText.objects.get(trstring=trstr, language=target).text == "Saluton"


def test_import_from_json_import_to(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language

    data = [
        {
            "path": "ui",
            "name": "hello",
            "translations": {source.code: {"text": "Hello"}},
        }
    ]
    uut.import_from_json(
        project,
        _json_file(data),
        update_texts=False,
        user_is_author=True,
        user=admin_user,
        import_to="app",
    )
    assert TrString.objects.filter(
        project=project, path="app/ui", name="hello"
    ).exists()


def test_import_from_json_wrong_format():
    with pytest.raises(WrongFormatError):
        uut.import_from_json(
            None,
            BytesIO(b"not json"),
            update_texts=False,
            user_is_author=False,
            user=None,
        )


def test_import_from_csv(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    target = lv.language

    fieldnames = ["path", "name", "pluralized", "context", source.code, target.code]
    rows = [
        {
            "path": "ui",
            "name": "hello",
            "pluralized": "0",
            "context": "",
            source.code: "Hello",
            target.code: "Saluton",
        }
    ]

    stats = uut.import_from_csv(
        project,
        _csv_file(fieldnames, rows),
        update_texts=False,
        user_is_author=True,
        user=admin_user,
    )
    assert stats == {"imported_strings": 1, "imported_translations": 1}

    trstr = TrString.objects.get(project=project, path="ui", name="hello")
    assert TrStringText.objects.get(trstring=trstr, language=target).text == "Saluton"


def test_import_from_csv_import_to(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language

    fieldnames = ["path", "name", source.code]
    rows = [{"path": "ui", "name": "hello", source.code: "Hello"}]

    uut.import_from_csv(
        project,
        _csv_file(fieldnames, rows),
        update_texts=False,
        user_is_author=True,
        user=admin_user,
        import_to="app",
    )
    assert TrString.objects.filter(
        project=project, path="app/ui", name="hello"
    ).exists()


def test_import_from_csv_wrong_format(admin_user):
    lv = LanguageVersionFactory()
    with pytest.raises(WrongFormatError):
        uut.import_from_csv(
            lv.project,
            BytesIO(b"name\nhello\n"),
            update_texts=False,
            user_is_author=False,
            user=admin_user,
        )


def test_import_from_po(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    lang = lv.language
    source = project.source_language

    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")
    TrStringTextFactory(trstring=trstr, language=lang, text="Saluton")

    po_data = export.export_to_po(project, languages=[lang.code])
    TrStringText.objects.filter(trstring=trstr, language=lang).delete()

    stats = uut.import_from_po(
        project,
        BytesIO(str(po_data[lang.code]).encode()),
        update_texts=False,
        user_is_author=True,
        user=admin_user,
    )
    assert stats == {"imported_strings": 0, "imported_translations": 1}
    assert TrStringText.objects.get(trstring=trstr, language=lang).text == "Saluton"


def test_import_from_po_pluralized(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    lang = lv.language
    source = project.source_language

    trstr = TrStringFactory(project=project, path="", name="item")
    TrStringTextFactory(trstring=trstr, language=source, pluralized=True)
    TrStringTextFactory(
        trstring=trstr,
        language=lang,
        pluralized=True,
        text='["wan", "tu"]',
    )

    po_data = export.export_to_po(project, languages=[lang.code])
    TrStringText.objects.filter(trstring=trstr, language=lang).delete()

    uut.import_from_po(
        project,
        BytesIO(str(po_data[lang.code]).encode()),
        update_texts=False,
        user_is_author=True,
        user=admin_user,
    )
    text = TrStringText.objects.get(trstring=trstr, language=lang)
    assert text.pluralized
    assert json.loads(text.text) == ["wan", "tu"]


def test_import_from_po_fuzzy(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    lang = lv.language
    source = project.source_language

    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")
    TrStringTextFactory(
        trstring=trstr, language=lang, text="Malnova", state=TRANSLATION_STATE_OUTDATED
    )

    po_data = export.export_to_po(project, languages=[lang.code], include_outdated=True)
    TrStringText.objects.filter(trstring=trstr, language=lang).delete()

    uut.import_from_po(
        project,
        BytesIO(str(po_data[lang.code]).encode()),
        update_texts=False,
        user_is_author=True,
        user=admin_user,
    )
    text = TrStringText.objects.get(trstring=trstr, language=lang)
    assert text.text == "Malnova"
    assert text.state == TRANSLATION_STATE_OUTDATED


def test_import_from_po_original_text_as_key(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    lang = lv.language
    source = project.source_language

    key = uut.text_to_key("Hello")
    trstr = TrStringFactory(project=project, path="", name=key)
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    po = polib.POFile()
    po.metadata = {"Language": lang.code, "Plural-Forms": lang.plural_forms}
    entry = polib.POEntry(msgid="Hello", msgstr="Saluton")
    po.append(entry)

    stats = uut.import_from_po(
        project,
        BytesIO(str(po).encode()),
        update_texts=False,
        user_is_author=True,
        user=admin_user,
        original_text_as_key=True,
    )
    assert stats == {"imported_strings": 0, "imported_translations": 1}
    assert TrStringText.objects.get(trstring=trstr, language=lang).text == "Saluton"


def test_import_from_nested_json(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language

    stats = uut.import_from_nested_json(
        project,
        _json_file({"hello": "Hello"}),
        source.code,
        update_texts=False,
        user_is_author=True,
        user=admin_user,
    )
    assert stats == {"imported_strings": 1, "imported_translations": 0}
    assert TrString.objects.filter(project=project, path="", name="hello").exists()


def test_import_from_nested_json_with_path(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    target = lv.language

    trstr = TrStringFactory(project=project, path="dir", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    stats = uut.import_from_nested_json(
        project,
        _json_file({"dir": {"hello": "Saluton"}}),
        target.code,
        update_texts=False,
        user_is_author=True,
        user=admin_user,
    )
    assert stats == {"imported_strings": 0, "imported_translations": 1}
    assert TrStringText.objects.get(trstring=trstr, language=target).text == "Saluton"


def test_import_from_nested_json_pluralized(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language

    uut.import_from_nested_json(
        project,
        _json_file({"item": "wan | tu"}),
        source.code,
        update_texts=False,
        user_is_author=True,
        user=admin_user,
    )
    text = TrStringText.objects.get(
        trstring__project=project, trstring__name="item", language=source
    )
    assert text.pluralized
    assert json.loads(text.text) == ["wan", "tu"]


def test_import_from_nested_json_export_default(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language

    content = 'export default {\n  "hello": "Hello"\n}'
    uut.import_from_nested_json(
        project,
        BytesIO(content.encode()),
        source.code,
        update_texts=False,
        user_is_author=True,
        user=admin_user,
    )
    assert TrString.objects.filter(project=project, name="hello").exists()


def test_import_from_nested_json_wrong_format():
    with pytest.raises(WrongFormatError):
        uut.import_from_nested_json(
            None,
            BytesIO(b"not json"),
            "eo",
            update_texts=False,
            user_is_author=False,
            user=None,
        )


def test_import_history_from_json(admin_user):
    lv = LanguageVersionFactory()
    text = TrStringTextFactory(
        trstring__project=lv.project,
        trstring__path="kronologio",
        trstring__name="1913-2",
        language=lv.language,
        translated_by=admin_user,
    )
    data = [
        {
            "name": text.trstring.name,
            "path": text.trstring.path,
            "language": text.language.code,
            "text": "24-31 août : 9e congrès mondial à Berne.",
            "datetime": "2017-04-10 10:09:43",
            "translated_by": admin_user.username,
        }
    ]

    imported = uut.import_history_from_json(text.trstring.project, _json_file(data))
    assert imported == 1
    assert TrStringTextHistory.objects.filter(
        trstringtext=text,
        text="24-31 août : 9e congrès mondial à Berne.",
    ).exists()


def test_import_history_from_json_skips_duplicate(admin_user):
    lv = LanguageVersionFactory()
    text = TrStringTextFactory(
        trstring__project=lv.project,
        trstring__path="ui",
        trstring__name="hello",
        language=lv.language,
    )
    data = [
        {
            "name": text.trstring.name,
            "path": text.trstring.path,
            "language": text.language.code,
            "text": "old version",
            "datetime": "2017-04-10 10:09:43",
            "translated_by": admin_user.username,
        }
    ]
    json_file = _json_file(data)

    assert uut.import_history_from_json(text.trstring.project, json_file) == 1
    assert uut.import_history_from_json(text.trstring.project, _json_file(data)) == 0

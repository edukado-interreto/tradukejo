import json

import pytest

from traduko import translation_functions as uut
from traduko.models import (
    ACTION_TYPE_ADD,
    STATE_FILTER_OUTDATED,
    STATE_FILTER_UNTRANSLATED,
    TRANSLATION_STATE_OUTDATED,
    TRANSLATION_STATE_TRANSLATED,
    StringActivity,
    TrString,
)
from traduko.tests.factories import (
    LanguageFactory,
    LanguageVersionFactory,
    ProjectFactory,
    StringActivityFactory,
    TrStringFactory,
    TrStringTextFactory,
)
from users.tests.factories import UserFactory


def test_atoi_and_natural_keys():
    assert uut.atoi("42") == 42
    assert uut.atoi("abc") == "abc"
    assert uut.natural_keys("item10") == ["item", 10, ""]


def test_parse_submitted_text_plain():
    res = uut.parse_submitted_text("  hello world  ", False, 2)
    assert res == {"text": "hello world", "words": 2, "characters": 11}


def test_parse_submitted_text_pluralized():
    data = json.dumps(
        [{"name": "text[0]", "value": "cat"}, {"name": "text[1]", "value": "cats"}]
    )
    res = uut.parse_submitted_text(data, True, 2)
    assert json.loads(res["text"]) == ["cat", "cats"]
    assert res["words"] == 2
    assert res["characters"] == 7


def test_parse_submitted_text_json_array():
    res = uut.parse_submitted_text(json.dumps(["alpha", "beta"]), True, 2)
    assert json.loads(res["text"]) == ["alpha", "beta"]


def test_get_text_difference():
    assert uut.get_text_difference("hello", "hallo") == "h<del>e</del><ins>a</ins>llo"


@pytest.mark.django_db
def test_is_project_admin(project_admin):
    project = project_admin.lv.project
    assert uut.is_project_admin(project_admin, project)
    assert not uut.is_project_admin(UserFactory(), project)


@pytest.mark.django_db
def test_is_allowed_to_translate(translator):
    project = translator.lv.project
    language = translator.lv.language
    project.visible = True
    project.locked = False
    project.save()

    assert uut.is_allowed_to_translate(translator, project, language)
    assert not uut.is_allowed_to_translate(UserFactory(), project, language)

    project.locked = True
    project.save()
    assert not uut.is_allowed_to_translate(translator, project, language)


@pytest.mark.django_db
def test_user_has_translation_right(translator):
    project = translator.lv.project
    assert uut.user_has_translation_right(translator, project)
    assert not uut.user_has_translation_right(UserFactory(), project)


@pytest.mark.django_db
def test_add_or_update_trstringtext_new_source_string(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language

    res = uut.add_or_update_trstringtext(
        project,
        "ui",
        "hello",
        source,
        "Hello",
        admin_user,
    )

    assert res["trstring"] is not None
    assert res["trstringtext"] is not None
    assert TrString.objects.filter(project=project, path="ui", name="hello").exists()
    assert StringActivity.objects.filter(
        trstringtext=res["trstringtext"], action=ACTION_TYPE_ADD
    ).exists()


@pytest.mark.django_db
def test_add_or_update_trstringtext_rejects_translation_without_source(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    target = lv.language

    res = uut.add_or_update_trstringtext(
        project,
        "ui",
        "hello",
        target,
        "Saluton",
        admin_user,
    )

    assert res == {"trstring": None, "trstringtext": None}


@pytest.mark.django_db
def test_add_or_update_trstringtext_marks_outdated(admin_user):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    target = lv.language

    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")
    target_text = TrStringTextFactory(
        trstring=trstr,
        language=target,
        text="Saluton",
        state=TRANSLATION_STATE_TRANSLATED,
    )

    uut.add_or_update_trstringtext(
        project,
        "ui",
        "hello",
        source,
        "New Hello",
        admin_user,
        minor=False,
    )

    target_text.refresh_from_db()
    assert target_text.state == TRANSLATION_STATE_OUTDATED


@pytest.mark.django_db
def test_mark_translations_as_outdated():
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    target = lv.language

    trstr = TrStringFactory(project=project)
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")
    target_text = TrStringTextFactory(
        trstring=trstr,
        language=target,
        state=TRANSLATION_STATE_TRANSLATED,
    )

    uut.mark_translations_as_outdated(trstr)
    target_text.refresh_from_db()
    assert target_text.state == TRANSLATION_STATE_OUTDATED


@pytest.mark.django_db
def test_filter_by_state():
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    target = lv.language

    trstr1 = TrStringFactory(project=project, name="untranslated")
    TrStringTextFactory(trstring=trstr1, language=source, text="A")
    trstr2 = TrStringFactory(project=project, name="outdated")
    TrStringTextFactory(trstring=trstr2, language=source, text="B")
    TrStringTextFactory(
        trstring=trstr2,
        language=target,
        text="B-old",
        state=TRANSLATION_STATE_OUTDATED,
    )

    trstrings = TrString.objects.filter(project=project)
    untranslated = uut.filter_by_state(trstrings, target, STATE_FILTER_UNTRANSLATED)
    assert set(untranslated.values_list("name", flat=True)) == {"untranslated"}

    outdated = uut.filter_by_state(trstrings, target, STATE_FILTER_OUTDATED)
    assert set(outdated.values_list("name", flat=True)) == {"outdated"}


@pytest.mark.django_db
def test_filter_by_search():
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    target = lv.language

    trstr = TrStringFactory(project=project, name="greeting", path="ui")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")
    TrStringTextFactory(trstring=trstr, language=target, text="Saluton")

    trstrings = TrString.objects.filter(project=project)
    by_name = uut.filter_by_search(trstrings, target, "greet")
    assert trstr in by_name

    by_translation = uut.filter_by_search(trstrings, target, "salut")
    assert trstr in by_translation


@pytest.mark.django_db
def test_addible_languages():
    project = ProjectFactory()
    project.needed_languages.clear()
    existing = LanguageVersionFactory(project=project)
    new_lang = LanguageFactory()

    addible = list(uut.addible_languages(project))
    codes = {lang.code for lang in addible}
    assert existing.language.code not in codes
    assert project.source_language.code not in codes
    assert new_lang.code in codes


@pytest.mark.django_db
def test_update_project_count():
    lv = LanguageVersionFactory(
        project__strings=0, project__words=0, project__characters=0
    )
    project = lv.project
    source = project.source_language
    trstr = TrStringFactory(project=project, words=3, characters=10)
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    uut.update_project_count(project)
    project.refresh_from_db()
    assert project.strings == 1
    assert project.words == 3
    assert project.characters == 10


@pytest.mark.django_db
def test_get_project_languages_for_user(translator, project_admin):
    project = translator.lv.project
    admin_langs = uut.get_project_languages_for_user(project, project_admin)
    translator_langs = uut.get_project_languages_for_user(project, translator)

    assert project.source_language in admin_langs
    assert translator.lv.language in translator_langs
    assert admin_langs.count() >= translator_langs.count()


@pytest.mark.django_db
def test_get_last_activities(admin_user):
    lv = LanguageVersionFactory()
    text = TrStringTextFactory(
        trstring__project=lv.project,
        language=lv.language,
    )
    StringActivityFactory(
        trstringtext=text,
        user=admin_user,
        language=lv.language,
    )

    activities = uut.get_last_activities(lv.project, limit=5)
    assert len(activities) >= 1

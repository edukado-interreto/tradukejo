from http import HTTPStatus
from unittest.mock import ANY

import pytest

from .factories import (
    CommentFactory,
    TrStringFactory,
    TrStringTextFactory,
    TrStringTextHistoryFactory,
)


def _json(data):
    return {"data": data, "content_type": "application/json"}


def translated_lang_dict(project, language=None):
    src = {project.source_language.code: project.source_language.name}
    return {language.code: language.name, **src} if language else src


def user_dict(user, lang="eo"):
    return {
        "id": user.pk,
        "username": user.username,
        "profile_url": f"/{lang}/user/{user.pk}/",
    }


@pytest.mark.django_db
def test_get_strings_empty(client, translator):
    project, language = translator.lv.project, translator.lv.language
    data = {"project_id": project.pk, "language": language.code}

    client.force_login(translator)
    resp = client.post("/eo/vue/get-strings/", **_json(data))

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"strings": [], "can_load_more": False}


@pytest.mark.django_db
def test_get_strings(client, translator):
    project, language = translator.lv.project, translator.lv.language
    trstring = TrStringFactory(project=project, name="nomo", path="ui")
    source = TrStringTextFactory(
        trstring=trstring, language=project.source_language, text="source"
    )
    trstringtext = TrStringTextFactory(
        trstring=trstring, language=language, text="translated"
    )
    TrStringTextHistoryFactory(trstringtext=trstringtext, translated_by=translator)
    CommentFactory(trstringtext=trstringtext, author=translator)

    data = {"project_id": project.pk, "language": language.code, "dir": "ui"}

    client.force_login(translator)
    resp = client.post("/eo/vue/get-strings/", **_json(data))

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "strings": [
            {
                "id": trstring.pk,
                "name": "nomo",
                "path": "ui",
                "context": trstring.context,
                "original_text": {
                    "id": source.pk,
                    "language": project.source_language.to_dict(),
                    "pluralized": False,
                    "raw_text": {
                        "1": "source",
                    },
                    "text": {
                        "1": "<p>source</p>",
                    },
                    "last_change": ANY,
                    "old_versions": 0,
                    "comments": 0,
                },
                "translated_text": {
                    "id": trstringtext.pk,
                    "language": language.to_dict(),
                    "pluralized": False,
                    "raw_text": {
                        "1": "translated",
                    },
                    "text": {
                        "1": "<p>translated</p>",
                    },
                    "last_change": ANY,
                    "old_versions": 1,
                    "comments": 1,
                },
                "state": 1,
                "translated_languages": translated_lang_dict(project, language),
            },
        ],
        "can_load_more": False,
    }


@pytest.mark.django_db
def test_get_directories_tree_simple(client, translator):
    project, language = translator.lv.project, translator.lv.language
    data = {"project_id": project.pk, "language": language.code}

    client.force_login(translator)
    resp = client.post("/eo/vue/get-directories-tree/", **_json(data))

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "directories_tree": {
            "": {
                "strings": {"count": 0, "words": 0, "characters": 0},
                "strings_in_children": {"count": 0, "words": 0, "characters": 0},
                "children": {},
            },
        }
    }


@pytest.mark.django_db
def test_get_string_translation(client, translator):
    project, language = translator.lv.project, translator.lv.language
    trstring = TrStringFactory(project=project)
    text = TrStringTextFactory(trstring=trstring, language=language, text="translated")
    data = {"trstring_id": trstring.pk, "language": language.code}

    client.force_login(translator)
    resp = client.post("/eo/vue/get-string-translation/", **_json(data))

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "id": text.pk,
        "language": language.to_dict(),
        "pluralized": False,
        "raw_text": {"1": "translated"},
        "text": {"1": "<p>translated</p>"},
        "last_change": ANY,
        "old_versions": 0,
        "comments": 0,
    }


@pytest.mark.django_db
def test_markoutdated(client, translator):
    project, language = translator.lv.project, translator.lv.language
    trstring = TrStringFactory(project=project)
    TrStringTextFactory(trstring=trstring, language=project.source_language, text="x")
    text = TrStringTextFactory(trstring=trstring, language=language, text="translated")

    client.force_login(translator)
    resp = client.post("/eo/vue/mark-outdated/", **_json({"trstringtext_id": text.pk}))

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"state": 2}


@pytest.mark.django_db
def test_marktranslated(client, translator):
    project, language = translator.lv.project, translator.lv.language
    trstring = TrStringFactory(project=project)
    TrStringTextFactory(trstring=trstring, language=project.source_language, text="x")
    text = TrStringTextFactory(trstring=trstring, language=language, text="translated")

    client.force_login(translator)
    resp = client.post(
        "/eo/vue/mark-translated/", **_json({"trstringtext_id": text.pk})
    )

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"state": 1}


@pytest.mark.django_db
def test_error_change_translation_state(client, project_admin):
    project = project_admin.lv.project

    trstring = TrStringFactory(project=project)
    text = TrStringTextFactory(
        trstring=trstring, language=project.source_language, text="x"
    )

    client.force_login(project_admin)
    resp = client.post(
        "/eo/vue/mark-translated/", **_json({"trstringtext_id": text.pk})
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.content.decode() == "Malĝusta ĉeno"


@pytest.mark.django_db
def test_delete_string(client, project_admin):
    trstring = TrStringFactory(project=project_admin.lv.project)

    client.force_login(project_admin)
    resp = client.post("/eo/vue/delete-string/", **_json({"trstring_id": trstring.pk}))

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"deleted": True}


@pytest.mark.django_db
def test_save_translation_new(client, translator):
    project, language = translator.lv.project, translator.lv.language
    trstring = TrStringFactory(project=project, name="n", context="ctx")
    text = TrStringTextFactory(
        trstring=trstring, language=project.source_language, text="old"
    )
    client.force_login(translator)
    resp = client.post(
        "/eo/vue/save-translation/",
        **_json(
            {"language": language.code, "trstring_id": trstring.pk, "text": ["nova"]}
        ),
    )

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "id": trstring.pk,
        "name": "n",
        "path": trstring.path,
        "context": "ctx",
        "original_text": {
            "id": text.pk,
            "language": project.source_language.to_dict(),
            "pluralized": False,
            "raw_text": {"1": "old"},
            "text": {"1": "<p>old</p>"},
            "last_change": ANY,
            "old_versions": 0,
            "comments": 0,
        },
        "translated_text": {
            "id": text.pk + 1,
            "language": language.to_dict(),
            "pluralized": False,
            "raw_text": {"1": "nova"},
            "text": {"1": "<p>nova</p>"},
            "last_change": ANY,
            "old_versions": 0,
            "comments": 0,
            "translated_by": user_dict(translator),
        },
        "state": 1,
        "translated_languages": translated_lang_dict(project, language),
    }


@pytest.mark.django_db
def test_save_translation_edit(client, translator):
    project = translator.lv.project
    language = project.source_language
    lv = project.languageversion_set.get(language=language)
    lv.translators.add(translator)
    trstring = TrStringFactory(project=project)
    text = TrStringTextFactory(trstring=trstring, language=language, text="x")

    client.force_login(translator)
    resp = client.post(
        "/eo/vue/save-translation/",
        **_json(
            {
                "language": language.code,
                "trstring_id": trstring.pk,
                "pluralized": False,
                "context": "ctx",
                "minor": True,
                "name": "nn",
                "path": "ui",
                "text": ["redaktite"],
            }
        ),
    )

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "id": trstring.pk,
        "name": "nn",
        "path": "ui",
        "context": trstring.context,
        "original_text": {
            "id": text.pk,
            "language": language.to_dict(),
            "pluralized": False,
            "raw_text": {"1": "redaktite"},
            "text": {"1": "<p>redaktite</p>"},
            "last_change": ANY,
            "old_versions": 1,
            "comments": 0,
            "translated_by": user_dict(translator),
        },
        "translated_text": {
            "id": text.pk,
            "language": language.to_dict(),
            "pluralized": False,
            "raw_text": {"1": "redaktite"},
            "text": {"1": "<p>redaktite</p>"},
            "last_change": ANY,
            "old_versions": 1,
            "comments": 0,
            "translated_by": user_dict(translator),
        },
        "state": 1,
        "translated_languages": {language.code: language.name},
    }


@pytest.mark.django_db
def test_add_string(client, project_admin):
    project = project_admin.lv.project
    client.force_login(project_admin)
    resp = client.post(
        "/eo/vue/add-string/",
        **_json(
            {
                "project_id": project.pk,
                "name": "n",
                "path": "",
                "pluralized": False,
                "context": "ctx",
                "text": ["nova"],
            }
        ),
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "id": ANY,
        "name": "n",
        "path": "",
        "context": "ctx",
        "original_text": {
            "id": ANY,
            "language": project.source_language.to_dict(),
            "pluralized": False,
            "raw_text": {"1": "nova"},
            "text": {"1": "<p>nova</p>"},
            "last_change": ANY,
            "old_versions": 0,
            "comments": 0,
            "translated_by": user_dict(project_admin),
        },
        "translated_text": {
            "id": ANY,
            "language": project.source_language.to_dict(),
            "pluralized": False,
            "raw_text": {"1": "nova"},
            "text": {"1": "<p>nova</p>"},
            "last_change": ANY,
            "old_versions": 0,
            "comments": 0,
            "translated_by": user_dict(project_admin),
        },
        "state": 1,
        "translated_languages": translated_lang_dict(project),
    }


@pytest.mark.django_db
def test_add_string_existing(client, project_admin):
    project = project_admin.lv.project
    trstring = TrStringFactory(project=project, name="nomo", path="ui")
    TrStringTextFactory(trstring=trstring, language=project.source_language)

    client.force_login(project_admin)
    resp = client.post(
        "/eo/vue/add-string/",
        **_json(
            {
                "project_id": project.pk,
                "name": "nomo",
                "path": "ui",
                "pluralized": False,
                "context": "ctx",
                "text": ["nova"],
            }
        ),
    )
    assert resp.status_code == HTTPStatus.CONFLICT
    assert resp.content.decode() == "Jam ekzistas ĉeno kun ĉi tiu nomo."


@pytest.mark.django_db
def test_get_history(client, translator):
    project = translator.lv.project
    trstring = TrStringFactory(project=project)
    text = TrStringTextFactory(
        trstring=trstring, language=project.source_language, text="ghi"
    )
    hist1 = TrStringTextHistoryFactory(
        trstringtext=text, translated_by=translator, text="abc"
    )
    hist2 = TrStringTextHistoryFactory(
        trstringtext=text, translated_by=translator, text="def"
    )

    client.force_login(translator)
    resp = client.post("/eo/vue/get-history/", **_json({"trstringtext_id": text.pk}))

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == [
        {
            "id": None,
            "pluralized": False,
            "create_date": ANY,
            "comparison": {"1": "<p><del>def</del><ins>ghi</ins></p>"},
        },
        {
            "id": hist2.pk,
            "pluralized": False,
            "create_date": ANY,
            "comparison": {"1": "<p><del>abc</del><ins>def</ins></p>"},
            "translated_by": user_dict(translator),
        },
        {
            "id": hist1.pk,
            "pluralized": False,
            "create_date": ANY,
            "comparison": {"1": "<p>abc</p>"},
            "translated_by": user_dict(translator),
        },
    ]


@pytest.mark.django_db
def test_get_comments(client, translator):
    project = translator.lv.project
    trstring = TrStringFactory(project=project)
    text = TrStringTextFactory(trstring=trstring, language=project.source_language)
    comment1 = CommentFactory(trstringtext=text, author=translator, text="klf?!?")
    comment2 = CommentFactory(trstringtext=text, author=translator, text="same")

    client.force_login(translator)
    resp = client.post("/eo/vue/get-comments/", **_json({"trstringtext_id": text.pk}))

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == [
        {
            "id": comment1.pk,
            "text": "klf?!?",
            "create_date": ANY,
            "author": user_dict(translator),
        },
        {
            "id": comment2.pk,
            "text": "same",
            "create_date": ANY,
            "author": user_dict(translator),
        },
    ]


@pytest.mark.django_db
def test_save_comments(client, translator):
    project = translator.lv.project
    trstring = TrStringFactory(project=project)
    text = TrStringTextFactory(trstring=trstring, language=project.source_language)

    client.force_login(translator)
    resp = client.post(
        "/eo/vue/save-comment/",
        **_json({"trstringtext_id": text.pk, "text": "klf?!?"}),
    )

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "id": ANY,
        "text": "klf?!?",
        "create_date": ANY,
        "author": user_dict(translator),
    }


@pytest.mark.django_db
def test_delete_comment(client, translator):
    project = translator.lv.project
    trstring = TrStringFactory(project=project)
    text = TrStringTextFactory(trstring=trstring, language=project.source_language)
    comment = CommentFactory(trstringtext=text, author=translator, text="")

    client.force_login(translator)
    resp = client.post("/eo/vue/delete-comment/", **_json({"comment_id": comment.pk}))

    assert text.comment_set.count() == 0
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"ok": True}


@pytest.mark.django_db
def test_get_translation_suggestions(client, translator):
    project, language = translator.lv.project, translator.lv.language

    trstring = TrStringFactory(project=project, name="tr")
    TrStringTextFactory(trstring=trstring, language=project.source_language, text="new")

    other = TrStringFactory(project=project)
    TrStringTextFactory(trstring=other, language=project.source_language, text="new")

    TrStringTextFactory(trstring=other, language=language, text="nova")

    client.force_login(translator)
    resp = client.post(
        "/eo/vue/get-translation-suggestions/",
        **_json({"trstring_id": trstring.pk, "language": language.code}),
    )

    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == [["nova"]]

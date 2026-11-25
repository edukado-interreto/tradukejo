import json
from http import HTTPStatus

import pytest
from dmr_jsonapi import JSON_API_CONTENT_TYPE

from traduko.models import TRANSLATION_STATE_OUTDATED
from traduko.tests.factories import (
    LanguageFactory,
    LanguageVersionFactory,
    ProjectFactory,
    TrStringFactory,
    TrStringTextFactory,
)
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

API = "/api/v3"


def _get(client, url, **params):
    resp = client.get(url, params, HTTP_ACCEPT=JSON_API_CONTENT_TYPE)
    assert resp["Content-Type"] == JSON_API_CONTENT_TYPE
    return resp, json.loads(resp.content)


def _error(body):
    (error,) = body["errors"]
    return error


@pytest.fixture
def project():
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    hello = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=hello, language=source, text="Hello")
    TrStringTextFactory(
        trstring=hello,
        language=lv.language,
        text="Saluton",
        state=TRANSLATION_STATE_OUTDATED,
    )
    items = TrStringFactory(project=project, path="", name="items")
    TrStringTextFactory(
        trstring=items,
        language=source,
        pluralized=True,
        text=json.dumps(["{n} item", "{n} items"]),
    )
    project.hello = hello
    project.items = items
    project.lv = lv
    return project


# Languages


def test_language_list(client):
    LanguageFactory(code="eo", name="Esperanto")
    LanguageFactory(code="sk", name="Slovenčina")

    resp, body = _get(client, f"{API}/languages/")

    assert resp.status_code == HTTPStatus.OK
    codes = [item["id"] for item in body["data"]]
    assert codes == sorted(codes)
    assert {"eo", "sk"} <= set(codes)
    assert body["meta"]["total"] == len(codes)
    assert body["links"]["first"].endswith("page%5Bnumber%5D=1&page%5Bsize%5D=100")


def test_language_detail(client):
    LanguageFactory(code="eo", name="Esperanto")

    resp, body = _get(client, f"{API}/languages/eo/")

    assert resp.status_code == HTTPStatus.OK
    assert body["data"]["type"] == "languages"
    assert body["data"]["id"] == "eo"
    assert body["data"]["attributes"]["name"] == "Esperanto"
    assert body["data"]["attributes"]["pluralExamples"][0].startswith("1")
    assert body["data"]["links"]["self"] == "http://testserver/api/v3/languages/eo/"


def test_language_not_found(client):
    resp, body = _get(client, f"{API}/languages/xx/")

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert _error(body) == {
        "status": "404",
        "code": "not_found",
        "detail": "Language not found",
    }


def test_language_cannot_include(client):
    LanguageFactory(code="eo")

    resp, body = _get(client, f"{API}/languages/eo/", include="projects")

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert _error(body)["source"] == {"parameter": "include"}


# Projects


def test_project_list_hides_invisible_projects(client, project):
    hidden = ProjectFactory(visible=False)

    resp, body = _get(client, f"{API}/projects/")

    assert resp.status_code == HTTPStatus.OK
    ids = [item["id"] for item in body["data"]]
    assert str(project.pk) in ids
    assert str(hidden.pk) not in ids
    assert "included" not in body


def test_project_list_shows_hidden_projects_to_admins(client):
    admin = UserFactory()
    hidden = ProjectFactory(visible=False, admins=[admin])
    client.force_login(admin)

    resp, body = _get(client, f"{API}/projects/")

    assert resp.status_code == HTTPStatus.OK
    assert str(hidden.pk) in [item["id"] for item in body["data"]]


def test_project_detail(client, project):
    resp, body = _get(client, f"{API}/projects/{project.pk}/")

    assert resp.status_code == HTTPStatus.OK
    data = body["data"]
    assert data["type"] == "projects"
    assert data["attributes"]["name"] == project.name
    assert data["relationships"]["sourceLanguage"]["data"] == {
        "type": "languages",
        "id": project.source_language_id,
    }
    assert "data" not in data["relationships"]["languageVersions"]
    assert data["relationships"]["strings"]["links"]["related"] == (
        f"http://testserver/api/v3/projects/{project.pk}/strings/"
    )
    assert body["links"]["self"] == f"http://testserver/api/v3/projects/{project.pk}/"


def test_project_detail_include(client, project):
    resp, body = _get(
        client,
        f"{API}/projects/{project.pk}/",
        include="sourceLanguage,languageVersions",
    )

    assert resp.status_code == HTTPStatus.OK
    relationships = body["data"]["relationships"]
    assert relationships["languageVersions"]["data"] == [
        {"type": "languageVersions", "id": str(project.lv.pk)}
    ]
    included = {(item["type"], item["id"]) for item in body["included"]}
    assert included == {
        ("languages", project.source_language_id),
        ("languageVersions", str(project.lv.pk)),
    }


def test_project_detail_hidden(client):
    hidden = ProjectFactory(visible=False)

    resp, body = _get(client, f"{API}/projects/{hidden.pk}/")

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert _error(body)["detail"] == "Project not found"


def test_project_detail_unknown_include(client, project):
    resp, body = _get(client, f"{API}/projects/{project.pk}/", include="admins")

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    error = _error(body)
    assert error["code"] == "invalid_include"
    assert "admins" in error["detail"]


# Language versions


def test_project_language_versions(client, project):
    resp, body = _get(
        client,
        f"{API}/projects/{project.pk}/language-versions/",
        include="language",
    )

    assert resp.status_code == HTTPStatus.OK
    (lv,) = body["data"]
    assert lv["id"] == str(project.lv.pk)
    assert "untranslatedWords" in lv["attributes"]
    assert lv["relationships"]["language"]["data"]["id"] == project.lv.language_id
    assert [item["id"] for item in body["included"]] == [project.lv.language_id]


def test_language_version_detail(client, project):
    resp, body = _get(client, f"{API}/language-versions/{project.lv.pk}/")

    assert resp.status_code == HTTPStatus.OK
    assert body["data"]["relationships"]["project"]["data"]["id"] == str(project.pk)


# Strings


def test_project_strings(client, project):
    resp, body = _get(client, f"{API}/projects/{project.pk}/strings/")

    assert resp.status_code == HTTPStatus.OK
    assert [item["attributes"]["name"] for item in body["data"]] == ["items", "hello"]
    assert body["meta"] == {"total": 2}


def test_project_strings_include_translations(client, project):
    resp, body = _get(
        client,
        f"{API}/projects/{project.pk}/strings/",
        include="translations",
        **{"filter[path]": "ui"},
    )

    assert resp.status_code == HTTPStatus.OK
    (hello,) = body["data"]
    assert hello["id"] == str(project.hello.pk)
    linkage = hello["relationships"]["translations"]["data"]
    assert len(linkage) == 2
    texts = {
        item["relationships"]["language"]["data"]["id"]: item["attributes"]
        for item in body["included"]
    }
    assert texts[project.source_language_id]["texts"] == ["Hello"]
    assert texts[project.lv.language_id]["texts"] == ["Saluton"]
    assert texts[project.lv.language_id]["state"] == "outdated"


def test_project_strings_pagination(client, project):
    resp, body = _get(
        client,
        f"{API}/projects/{project.pk}/strings/",
        **{"page[number]": "2", "page[size]": "1"},
    )

    assert resp.status_code == HTTPStatus.OK
    assert [item["id"] for item in body["data"]] == [str(project.hello.pk)]
    assert body["links"]["next"] is None
    assert body["links"]["prev"].endswith("page%5Bnumber%5D=1&page%5Bsize%5D=1")


def test_project_strings_page_out_of_range(client, project):
    resp, body = _get(
        client,
        f"{API}/projects/{project.pk}/strings/",
        **{"page[number]": "3", "page[size]": "1"},
    )

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert _error(body)["source"] == {"parameter": "page[number]"}


@pytest.mark.parametrize(
    "params",
    [
        {"page[size]": "0"},
        {"page[size]": "1001"},
        {"page[number]": "first"},
        {"sort": "name"},
    ],
)
def test_project_strings_invalid_query(client, project, params):
    resp, body = _get(client, f"{API}/projects/{project.pk}/strings/", **params)

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    error = _error(body)
    assert error["status"] == "400"
    assert error["source"] == {"parameter": next(iter(params))}
    assert "meta" not in error


def test_string_detail(client, project):
    resp, body = _get(client, f"{API}/strings/{project.hello.pk}/", include="project")

    assert resp.status_code == HTTPStatus.OK
    assert body["data"]["attributes"]["path"] == "ui"
    assert body["included"][0]["type"] == "projects"


def test_string_of_hidden_project(client):
    trstring = TrStringFactory(project=ProjectFactory(visible=False))

    resp, _ = _get(client, f"{API}/strings/{trstring.pk}/")

    assert resp.status_code == HTTPStatus.NOT_FOUND


# Translations


def test_string_translations(client, project):
    resp, body = _get(
        client,
        f"{API}/strings/{project.hello.pk}/translations/",
        **{"filter[language]": project.lv.language_id},
    )

    assert resp.status_code == HTTPStatus.OK
    (translation,) = body["data"]
    assert translation["attributes"]["texts"] == ["Saluton"]


def test_translation_detail_pluralized(client, project):
    text = project.items.trstringtext_set.get()

    resp, body = _get(client, f"{API}/translations/{text.pk}/", include="string")

    assert resp.status_code == HTTPStatus.OK
    attributes = body["data"]["attributes"]
    assert attributes["pluralized"] is True
    assert attributes["texts"] == ["{n} item", "{n} items"]
    assert body["included"][0]["id"] == str(project.items.pk)


# Protocol


def test_unsupported_accept_parameters(client):
    resp = client.get(
        f"{API}/languages/", HTTP_ACCEPT=f"{JSON_API_CONTENT_TYPE}; charset=utf-8"
    )

    assert resp.status_code == HTTPStatus.NOT_ACCEPTABLE


def test_method_not_allowed(client):
    resp = client.post(f"{API}/languages/", HTTP_ACCEPT=JSON_API_CONTENT_TYPE)

    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    assert _error(json.loads(resp.content))["status"] == "405"


def test_unknown_url(client):
    resp, body = _get(client, f"{API}/nothing/")

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert _error(body) == {
        "status": "404",
        "code": "not_found",
        "detail": "Page not found",
    }


def test_v1_unknown_url_keeps_its_format(client):
    resp = client.get("/api/nothing/")

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert "detail" in resp.json()


def test_schema(client):
    resp = client.get(f"{API}/schema")

    assert resp.status_code == HTTPStatus.OK
    schema = resp.json()
    assert schema["info"]["version"] == "3.0"
    assert "/api/v3/projects/{pk}/strings/" in schema["paths"]
    assert "/api/project/{pk}/export/" not in schema["paths"]


@pytest.mark.parametrize("page", ["docs", "swagger"])
def test_docs_pages(client, page):
    resp = client.get(f"{API}/{page}")

    assert resp.status_code == HTTPStatus.OK

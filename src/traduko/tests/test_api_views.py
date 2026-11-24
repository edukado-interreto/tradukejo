import json
from http import HTTPStatus

import pytest
from traduko.tests.factories import (
    LanguageVersionFactory,
    TrStringFactory,
    TrStringTextFactory,
)


pytestmark = pytest.mark.django_db


def _body(resp) -> bytes:
    """File responses are streamed, read them the same way the client does."""
    if resp.streaming:
        return b"".join(resp.streaming_content)
    return resp.content


def test_language_list(dmr_client):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language

    resp = dmr_client.get(f"/api/project/{project.pk}/languages/")

    assert resp.status_code == HTTPStatus.OK
    codes = {item["code"] for item in resp.json()}
    assert source.code in codes
    assert lv.language.code in codes


def test_export_simple_json(dmr_client):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    resp = dmr_client.get(
        f"/api/project/{project.pk}/export/",
        HTTP_ACCEPT="application/json",
    )

    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data[0]["name"] == "hello"
    assert data[0]["translations"][source.code]["text"] == "Hello"


def test_export_simple_csv(dmr_client):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    resp = dmr_client.get(
        f"/api/project/{project.pk}/export/",
        HTTP_ACCEPT="text/csv",
    )

    assert resp.status_code == HTTPStatus.OK
    assert resp["Content-Type"].startswith("text/csv")
    assert "path,name" in _body(resp).decode()


def test_export_po_requires_one_language(dmr_client):
    lv = LanguageVersionFactory()
    project = lv.project

    resp = dmr_client.get(
        f"/api/project/{project.pk}/export/",
        HTTP_ACCEPT="application/po",
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "languages" in json.dumps(resp.json()).lower()


def test_export_po_single_language(dmr_client):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    resp = dmr_client.get(
        f"/api/project/{project.pk}/export/?languages={source.code}",
        HTTP_ACCEPT="application/po",
    )

    assert resp.status_code == HTTPStatus.OK
    assert b"msgid" in _body(resp)


def test_export_nested_not_acceptable(dmr_client):
    lv = LanguageVersionFactory()
    project = lv.project

    resp = dmr_client.get(
        f"/api/project/{project.pk}/export/nested/",
        HTTP_ACCEPT="text/csv",
    )

    assert resp.status_code == HTTPStatus.NOT_ACCEPTABLE


def test_language_list_missing_project(dmr_client):
    resp = dmr_client.get("/api/project/999999/languages/")

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert resp.json()["detail"]


def test_export_po_single_language_has_header(dmr_client):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    resp = dmr_client.get(
        f"/api/project/{project.pk}/export/po/{project.pk}.po?languages={source.code}"
    )

    assert resp.status_code == HTTPStatus.OK
    assert _body(resp).startswith(b'#\nmsgid ""\nmsgstr ""')


def test_schema_is_served(dmr_client):
    resp = dmr_client.get("/api/schema")

    assert resp.status_code == HTTPStatus.OK
    assert "/api/project/{pk}/export/" in resp.json()["paths"]

import json
from http import HTTPStatus

import pytest
from rest_framework.test import APIClient

from traduko.tests.factories import (
    LanguageVersionFactory,
    TrStringFactory,
    TrStringTextFactory,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_language_list(api_client):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language

    resp = api_client.get(f"/api/project/{project.pk}/languages/")

    assert resp.status_code == HTTPStatus.OK
    codes = {item["code"] for item in resp.json()}
    assert source.code in codes
    assert lv.language.code in codes


@pytest.mark.django_db
def test_export_simple_json(api_client):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    resp = api_client.get(
        f"/api/project/{project.pk}/export/",
        HTTP_ACCEPT="application/json",
    )

    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data[0]["name"] == "hello"
    assert data[0]["translations"][source.code]["text"] == "Hello"


@pytest.mark.django_db
def test_export_simple_csv(api_client):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    resp = api_client.get(
        f"/api/project/{project.pk}/export/",
        HTTP_ACCEPT="text/csv",
    )

    assert resp.status_code == HTTPStatus.OK
    assert resp["Content-Type"].startswith("text/csv")
    assert "path,name" in resp.content.decode()


@pytest.mark.django_db
def test_export_po_requires_one_language(api_client):
    lv = LanguageVersionFactory()
    project = lv.project

    resp = api_client.get(
        f"/api/project/{project.pk}/export/",
        HTTP_ACCEPT="application/po",
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "languages" in json.dumps(resp.json()).lower()


@pytest.mark.django_db
def test_export_po_single_language(api_client):
    lv = LanguageVersionFactory()
    project = lv.project
    source = project.source_language
    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    resp = api_client.get(
        f"/api/project/{project.pk}/export/?languages={source.code}",
        HTTP_ACCEPT="application/po",
    )

    assert resp.status_code == HTTPStatus.OK
    assert b"msgid" in resp.content


@pytest.mark.django_db
def test_export_nested_not_acceptable(api_client):
    lv = LanguageVersionFactory()
    project = lv.project

    resp = api_client.get(
        f"/api/project/{project.pk}/export/nested/",
        HTTP_ACCEPT="text/csv",
    )

    assert resp.status_code == HTTPStatus.NOT_ACCEPTABLE

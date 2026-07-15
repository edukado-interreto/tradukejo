import json
from http import HTTPStatus

import pytest

from traduko.models import LanguageVersion, TranslatorRequest
from traduko.tests.factories import (
    LanguageFactory,
    LanguageVersionFactory,
    TranslatorRequestFactory,
)
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_request_translator_permission_requires_login(client):
    project = LanguageVersionFactory().project
    language = LanguageFactory()
    resp = client.post(
        f"/eo/ajax/request-translator-permission/{project.pk}/",
        {"language": language.pk, "explanation": "Mi volas traduki."},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert "/login" in resp.url


@pytest.mark.django_db
def test_request_translator_permission_creates_request(client):
    user = UserFactory()
    lv = LanguageVersionFactory()
    project = lv.project
    language = LanguageFactory()

    client.force_login(user)
    resp = client.post(
        f"/eo/ajax/request-translator-permission/{project.pk}/",
        {"language": language.pk, "explanation": "Mi volas traduki."},
    )

    assert resp.status_code == HTTPStatus.OK
    data = json.loads(resp.content)
    assert "message" in data
    assert "button" in data
    assert TranslatorRequest.objects.filter(user=user).exists()
    assert LanguageVersion.objects.filter(project=project, language=language).exists()


@pytest.mark.django_db
def test_request_translator_permission_already_translator(client, translator):
    project = translator.lv.project
    language = translator.lv.language

    client.force_login(translator)
    resp = client.post(
        f"/eo/ajax/request-translator-permission/{project.pk}/",
        {"language": language.pk, "explanation": ""},
    )

    data = json.loads(resp.content)
    assert TranslatorRequest.objects.filter(user=translator).count() == 0
    assert "button" in data


@pytest.mark.django_db
def test_request_translator_permission_duplicate(client):
    user = UserFactory()
    req = TranslatorRequestFactory(user=user)

    client.force_login(user)
    resp = client.post(
        f"/eo/ajax/request-translator-permission/{req.language_version.project.pk}/",
        {
            "language": req.language_version.language.pk,
            "explanation": "Denove",
        },
    )

    data = json.loads(resp.content)
    assert TranslatorRequest.objects.filter(user=user).count() == 1
    assert "button" in data

import json
from http import HTTPStatus

import pytest
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile

from traduko.models import LanguageVersion, TranslatorRequest, TrString
from traduko.tests.factories import (
    TranslatorRequestFactory,
    TrStringFactory,
    TrStringTextFactory,
)
from users.tests.factories import UserFactory


def _csv_upload(content, name="import.csv"):
    return SimpleUploadedFile(name, content.encode("utf-8"), content_type="text/csv")


@pytest.mark.django_db
def test_translator_request_list_requires_admin(client, translator):
    project = translator.lv.project
    client.force_login(translator)
    resp = client.get(f"/eo/project/{project.pk}/translator-requests/")
    assert resp.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_translator_request_list(client, project_admin):
    project = project_admin.lv.project
    req = TranslatorRequestFactory(language_version=project_admin.lv)

    client.force_login(project_admin)
    resp = client.get(f"/eo/project/{project.pk}/translator-requests/")

    assert resp.status_code == HTTPStatus.OK
    assert req in resp.context["requests"]


@pytest.mark.django_db
def test_accept_translator_request(client, project_admin):
    req = TranslatorRequestFactory(
        language_version__project=project_admin.lv.project,
        user=UserFactory(),
    )
    project_id = req.language_version.project.pk
    request_id = req.pk

    client.force_login(project_admin)
    resp = client.get(f"/eo/project/accept-translator-request/{request_id}/")

    assert resp.status_code == HTTPStatus.FOUND
    assert resp.url.endswith(f"/project/{project_id}/translator-requests/")
    assert not TranslatorRequest.objects.filter(pk=request_id).exists()
    lv = LanguageVersion.objects.get(pk=req.language_version.pk)
    assert req.user in lv.translators.all()
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_decline_translator_request_deletes_language_version(client, project_admin):
    req = TranslatorRequestFactory(
        language_version__project=project_admin.lv.project,
        user=UserFactory(),
    )
    lv_id = req.language_version.pk
    project_id = req.language_version.project.pk

    client.force_login(project_admin)
    resp = client.get(f"/eo/project/decline-translator-request/{req.pk}/")

    assert resp.status_code == HTTPStatus.FOUND
    assert resp.url.endswith(f"/project/{project_id}/translator-requests/")
    assert not LanguageVersion.objects.filter(pk=lv_id).exists()
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_decline_translator_request_keeps_language_version(client, project_admin):
    req = TranslatorRequestFactory(
        language_version__project=project_admin.lv.project,
        user=UserFactory(),
    )
    lv = req.language_version
    TrStringTextFactory(
        trstring__project=lv.project,
        language=lv.language,
    )

    client.force_login(project_admin)
    client.get(f"/eo/project/decline-translator-request/{req.pk}/")

    assert LanguageVersion.objects.filter(pk=lv.pk).exists()
    assert not TranslatorRequest.objects.filter(pk=req.pk).exists()


@pytest.mark.django_db
def test_import_csv(client, project_admin):
    project = project_admin.lv.project
    source = project.source_language
    csv_content = f"path,name,{source.code}\nui,hello,Hello\n"

    client.force_login(project_admin)
    resp = client.post(
        f"/eo/project/{project.pk}/import/csv/",
        {
            "file": _csv_upload(csv_content),
            "import_to": "",
            "update_texts": "",
            "user_is_author": "on",
        },
    )

    assert resp.status_code == HTTPStatus.OK
    assert TrString.objects.filter(project=project, path="ui", name="hello").exists()


@pytest.mark.django_db
def test_import_csv_wrong_extension(client, project_admin):
    project = project_admin.lv.project
    source = project.source_language
    csv_content = f"path,name,{source.code}\nui,hello,Hello\n"

    client.force_login(project_admin)
    resp = client.post(
        f"/eo/project/{project.pk}/import/csv/",
        {
            "file": _csv_upload(csv_content, name="import.txt"),
            "import_to": "",
        },
    )

    assert resp.status_code == HTTPStatus.OK
    assert not TrString.objects.filter(project=project).exists()


@pytest.mark.django_db
def test_export_json(client, project_admin):
    project = project_admin.lv.project
    source = project.source_language
    trstr = TrStringFactory(project=project, path="ui", name="hello")
    TrStringTextFactory(trstring=trstr, language=source, text="Hello")

    client.force_login(project_admin)
    resp = client.post(f"/eo/project/{project.pk}/export/json/", {})

    assert resp.status_code == HTTPStatus.OK
    assert resp["Content-Disposition"].startswith('attachment; filename="')
    data = json.loads(resp.content)
    assert data[0]["name"] == "hello"


@pytest.mark.django_db
def test_import_export_page(client, project_admin):
    project = project_admin.lv.project
    client.force_login(project_admin)
    resp = client.get(f"/eo/project/{project.pk}/import-export/")
    assert resp.status_code == HTTPStatus.OK
    assert resp.context["project"] == project

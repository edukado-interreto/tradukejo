import json
from http import HTTPStatus
from unittest.mock import patch

import pytest

from traduko.models import LanguageVersion
from traduko.tests.factories import (
    LanguageFactory,
    LanguageVersionFactory,
    ProjectFactory,
    TranslatorRequestFactory,
)


@pytest.mark.django_db
def test_projects_visible_to_anonymous(client):
    visible = ProjectFactory(visible=True)
    hidden = ProjectFactory(visible=False)

    resp = client.get("/eo/")

    assert resp.status_code == HTTPStatus.OK
    projects = list(resp.context["projects"])
    assert visible in projects
    assert hidden not in projects


@pytest.mark.django_db
def test_projects_admin_sees_hidden(client, project_admin):
    hidden = ProjectFactory(visible=False)
    project_admin.lv.project.admins.add(project_admin)

    client.force_login(project_admin)
    resp = client.get("/eo/")

    assert hidden in list(resp.context["projects"])


@pytest.mark.django_db
def test_projectpage_hidden_for_non_admin(client, translator):
    project = ProjectFactory(visible=False, admins=[])
    project.admins.clear()

    client.force_login(translator)
    resp = client.get(f"/eo/project/{project.pk}/")
    assert resp.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_projectpage_for_admin(client, project_admin):
    project = project_admin.lv.project

    client.force_login(project_admin)
    resp = client.get(f"/eo/project/{project.pk}/")

    assert resp.status_code == HTTPStatus.OK
    assert resp.context["is_project_admin"] is True
    assert resp.context["project"] == project


@pytest.mark.django_db
def test_projectpage_translator_request_count(client, project_admin):
    project = project_admin.lv.project
    TranslatorRequestFactory(language_version__project=project)

    client.force_login(project_admin)
    resp = client.get(f"/eo/project/{project.pk}/")

    assert resp.context["translator_request_count"] == 1


@pytest.mark.django_db
def test_translate_requires_login(client):
    project = LanguageVersionFactory().project
    resp = client.get(f"/eo/translate/{project.pk}/")
    assert resp.status_code == HTTPStatus.FOUND
    assert "/login" in resp.url


@pytest.mark.django_db
@patch("traduko.views.finders.find", return_value="/tmp/vue-static")
@patch("traduko.views.os.walk")
def test_translate_renders(mock_walk, mock_find, client, translator):
    mock_walk.return_value = [("/tmp/vue-static", [], ["app.js", "chunk.js"])]
    project = translator.lv.project

    client.force_login(translator)
    resp = client.get(f"/eo/translate/{project.pk}/")

    assert resp.status_code == HTTPStatus.OK
    languages = json.loads(resp.context["available_languages"])
    assert any(lang["code"] == translator.lv.language.code for lang in languages)
    assert resp.context["csrf"]


@pytest.mark.django_db
def test_add_language_version_as_admin(client, project_admin):
    project = project_admin.lv.project
    lang = LanguageFactory()

    client.force_login(project_admin)
    resp = client.get(f"/eo/project/{project.pk}/add-language-version/{lang.code}/")

    assert resp.status_code == HTTPStatus.FOUND
    assert LanguageVersion.objects.filter(project=project, language=lang).exists()


@pytest.mark.django_db
def test_add_language_version_ignored_for_non_admin(client, translator):
    project = translator.lv.project
    lang = LanguageFactory()

    client.force_login(translator)
    resp = client.get(f"/eo/project/{project.pk}/add-language-version/{lang.code}/")

    assert resp.status_code == HTTPStatus.FOUND
    assert not LanguageVersion.objects.filter(project=project, language=lang).exists()

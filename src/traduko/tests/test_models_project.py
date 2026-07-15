import pytest

from traduko.models import project_image_upload_location

from .factories import LanguageVersionFactory, ProjectFactory, TranslatorRequestFactory


def test_project_str():
    project = ProjectFactory.build()
    assert str(project) == project.name


def test_project_image_upload_location():
    project = ProjectFactory.build()
    project.pk = 42
    location = project_image_upload_location(project, "logo.png")
    assert location == "projects/42.png"


def test_language_version_str():
    lv = LanguageVersionFactory.build()
    assert str(lv) == lv.project.name + " - " + lv.language.code


@pytest.mark.django_db
def test_language_version_methods():
    project = ProjectFactory(strings=9, words=16, characters=99)
    lv = LanguageVersionFactory.build(
        project=project,
        translated_strings=4,
        translated_words=9,
        translated_characters=48,
        outdated_strings=2,
        outdated_words=3,
        outdated_characters=30,
    )

    assert lv.untranslated_strings() == 3
    assert lv.untranslated_words() == 4
    assert lv.untranslated_characters() == 21
    assert lv.translated_percent() == 56.25
    assert lv.outdated_percent() == 18.75
    assert lv.untranslated_percent() == 25.0


@pytest.mark.django_db
def test_translator_request_str():
    tr = TranslatorRequestFactory()
    assert str(tr) == tr.user.username + " - " + str(tr.language_version)

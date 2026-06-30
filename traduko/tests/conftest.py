import pytest

from users.tests.factories import UserFactory

from .factories import LanguageFactory, LanguageVersionFactory, ProjectFactory


@pytest.fixture
def translator():
    user = UserFactory()
    source_lang = LanguageFactory()
    project = ProjectFactory(source_language=source_lang)
    project.admins.clear()
    LanguageVersionFactory(project=project, language=source_lang)
    target_lang = LanguageFactory()
    lv = LanguageVersionFactory(project=project, language=target_lang)
    lv.translators.add(user)
    user.lv = lv
    return user


@pytest.fixture
def project_admin(translator):
    project = translator.lv.project
    project.admins.add(translator)
    project.save()
    return translator

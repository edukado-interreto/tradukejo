import pytest
from freezegun import freeze_time

from traduko.models import TrString, TrStringText

from .factories import (
    LanguageFactory,
    LanguageVersionFactory,
    ProjectFactory,
    TrStringFactory,
    TrStringTextFactory,
)


@pytest.mark.django_db
def test_tr_string_manager():
    en = LanguageFactory()
    eo = LanguageFactory()
    project = ProjectFactory(source_language=en)
    LanguageVersionFactory(project=project, language=en)
    LanguageVersionFactory(project=project, language=eo)

    TrStringTextFactory(trstring__project=project, language=en, text="One")

    TrStringTextFactory(trstring__project=project, language=en, text="Two")

    TrStringTextFactory(trstring__project=project, language=en, text="Three")

    assert TrString.objects.count() == 3
    assert TrStringText.objects.count() == 3

    qs = TrString.objects.untranslated(project, eo)
    assert qs.count() == 3
    assert set(qs.values_list("source_text", flat=True)) == {"One", "Two", "Three"}


def test_tr_string_str():
    tr_str = TrStringFactory.build(path="ui", name="nomo")
    assert str(tr_str) == "ui#nomo"


@pytest.mark.django_db
def test_tr_string_to_dict():
    class Text:
        def __init__(self, text):
            self.text = text
            self.state = 1

        def to_dict(self):
            return {"text": self.text}

    tr_str = TrStringFactory(path="ui", name="nomo", context="ctx")
    assert tr_str.to_dict() == {
        "id": tr_str.pk,
        "name": "nomo",
        "path": "ui",
        "context": "ctx",
        "translated_text": None,
        "translated_languages": {},
        "state": 0,
    }

    lv = LanguageVersionFactory(project=tr_str.project)
    TrStringTextFactory(trstring=tr_str, language=lv.language)
    original, translated = Text("original"), Text("translated")

    assert tr_str.to_dict(original, translated) == {
        "id": tr_str.pk,
        "name": "nomo",
        "path": "ui",
        "context": "ctx",
        "original_text": {"text": "original"},
        "translated_text": {"text": "translated"},
        "translated_languages": {lv.language.code: lv.language.name},
        "state": 1,
    }


def test_tr_string_text_str():
    tr_str = TrStringFactory.build(path="ui", name="nomo")
    text = TrStringTextFactory.build(trstring=tr_str, text="teksto")
    assert str(text) == "ui#nomo ‑ " + text.language.code


@pytest.mark.django_db
@freeze_time("1887-07-14 10:30")
def test_tr_string_text_to_dict():
    tr_str = TrStringFactory(path="ui", name="nomo")
    lv = LanguageVersionFactory(project=tr_str.project)
    text = TrStringTextFactory(trstring=tr_str, language=lv.language, text="teksto")
    assert text.to_dict() == {
        "id": text.pk,
        "language": lv.language.to_dict(),
        "pluralized": False,
        "raw_text": {"1": "teksto"},
        "text": {"1": "<p>teksto</p>"},
        "last_change": "14-a de julio 1887, je 10:30",
        "old_versions": 0,
        "comments": 0,
    }

from .factories import LanguageFactory


def test_language_str():
    lang = LanguageFactory.build(code="eo", name="Esperanto")
    assert str(lang) == "eo - Esperanto"


def test_language_defaults():
    lang = LanguageFactory.build(code="eo")
    assert lang.code == "eo"
    assert lang.direction == "ltr"
    assert not lang.google
    assert not lang.yandex
    assert not lang.deepl


def test_language_plural_forms():
    plural_forms_ru = (
        "nplurals=3; plural=("
        "n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2"
        ");"
    )
    lang = LanguageFactory.build(plural_forms=plural_forms_ru)
    assert lang.nplurals() == 3
    assert lang.plural_examples_list() == [
        "1, 21, 31, 41, 51…",
        "2, 3, 4, 22, 23…",
        "0, 5, 6, 7, 8…",
    ]

    plural_forms_ar = (
        "nplurals=6; plural=("
        "n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5"
        ");"
    )
    lang = LanguageFactory.build(plural_forms=plural_forms_ar)
    assert lang.nplurals() == 6
    assert lang.plural_examples_list() == [
        "0",
        "1",
        "2",
        "3, 4, 5, 6, 7…",
        "11, 12, 13, 14, 15…",
        "100, 101, 102…",
    ]


def test_language_to_dict():
    lang = LanguageFactory.build(
        code="en",
        direction="rtl",
        google=True,
        yandex=True,
        deepl=True,
        plural_forms="nplurals=2; plural=(n == 1 ? 0 : 1);",
    )
    assert lang.to_dict() == {
        "code": "en",
        "name": lang.name,
        "direction": "rtl",
        "google": True,
        "yandex": True,
        "deepl": True,
        "plural_examples_list": ["1", "0, 2, 3, 4, 5…"],
    }

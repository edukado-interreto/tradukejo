from model_bakery import baker

nplurals_min = "nplurals=2; plural=(n == 1 ? 0 : 1);"
nplurals_ru = "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)"


def test_language_str():
    lang = baker.prepare("traduko.Language", code="eo", name="Esperanto")
    assert str(lang) == "eo - Esperanto"

def test_language_defaults():
    lang = baker.prepare("traduko.Language", code="eo")
    assert lang.code == "eo"
    assert lang.direction == "ltr"
    assert not lang.google
    assert not lang.yandex
    assert not lang.deepl


def test_language_plural_forms():
    lang = baker.prepare("traduko.Language", code="eo", plural_forms=nplurals_ru)
    assert lang.nplurals() == 3
    assert lang.plural_examples_list() == [
        "1, 21, 31, 41, 51…",
        "2, 3, 4, 22, 23…",
        "0, 5, 6, 7, 8…",
    ]


def test_language_to_dict():
    lang = baker.prepare(
        "traduko.Language",
        code="en",
        direction="rtl",
        google=True,
        yandex=True,
        deepl=True,
        plural_forms=nplurals_min,
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

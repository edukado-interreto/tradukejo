import json
from unittest.mock import MagicMock, patch

import pytest

from traduko import deepl as uut
from traduko.tests.factories import LanguageFactory, ProjectFactory
from users.tests.factories import DeeplAuthKeyFactory


@pytest.mark.django_db
def test_fetch_deepl_without_auth_key():
    assert uut.fetch_deepl("usage") is None


@pytest.mark.django_db
@patch("traduko.deepl.DeeplAuthKey.get_least_used")
@patch("traduko.deepl._fetch_deepl")
def test_fetch_deepl_uses_least_used_key(mock_fetch, mock_get_least):
    key = DeeplAuthKeyFactory(
        api_key="11111111-1111-4111-8111-111111111111:fx",
        character_count=10,
    )
    mock_get_least.return_value = key
    mock_fetch.return_value = MagicMock(
        code=200, read=lambda: json.dumps({"character_count": 0}).encode()
    )

    uut.fetch_deepl("usage")

    mock_get_least.assert_called_once()
    assert mock_fetch.call_args[0][0] == key


@pytest.mark.django_db
@patch("traduko.deepl.update_deepl_usage")
@patch("traduko.deepl._fetch_deepl")
def test_deepl_usage_updates_even_on_error(mock_fetch, mock_update):
    key = DeeplAuthKeyFactory.build()
    mock_fetch.side_effect = RuntimeError("network")

    with pytest.raises(RuntimeError):
        with uut.deepl_usage(key):
            raise RuntimeError("network")

    mock_update.assert_called_once_with(key)


@pytest.mark.django_db
@patch("traduko.deepl._fetch_deepl")
def test_update_deepl_usage(mock_fetch):
    key = DeeplAuthKeyFactory(character_count=0)
    mock_fetch.return_value = MagicMock(
        code=200, read=lambda: json.dumps({"character_count": 42}).encode()
    )

    uut.update_deepl_usage(key)
    key.refresh_from_db()
    assert key.character_count == 42


@pytest.mark.django_db
@patch("traduko.deepl._fetch_deepl")
def test_update_deepl_usage_skips_non_200(mock_fetch):
    key = DeeplAuthKeyFactory(character_count=5)
    mock_fetch.return_value = MagicMock(code=403, read=lambda: b"")

    uut.update_deepl_usage(key)
    key.refresh_from_db()
    assert key.character_count == 5


@pytest.mark.django_db
@patch("traduko.deepl.fetch_deepl")
def test_fetch_deepl_translate(mock_fetch):
    project = ProjectFactory()
    language = LanguageFactory()
    mock_fetch.return_value = MagicMock(
        code=200,
        read=lambda: json.dumps(
            {"translations": [{"text": "saluton", "detected_source_language": "EN"}]}
        ).encode(),
    )

    result = uut.fetch_deepl_translate(project, "hello", language)

    assert result == {
        "translations": [{"text": "saluton", "detected_source_language": "EN"}]
    }
    payload = mock_fetch.call_args[0][1]
    assert payload["text"] == ["hello"]
    assert payload["target_lang"] == language.code
    assert payload["source_lang"] == project.source_language.code
    assert payload["context"] == project.description


@pytest.mark.django_db
@patch("traduko.deepl.fetch_deepl_translate")
def test_deepl_translate(mock_fetch):
    project = ProjectFactory()
    language = LanguageFactory()
    mock_fetch.return_value = {
        "translations": [{"text": "unua"}, {"text": "dua"}],
    }

    assert uut.deepl_translate(project, ["hello", "world"], language) == ["unua", "dua"]


@pytest.mark.django_db
@patch("traduko.deepl.fetch_deepl_translate", return_value=None)
def test_deepl_translate_on_failure(mock_fetch):
    project = ProjectFactory()
    language = LanguageFactory()
    assert uut.deepl_translate(project, "hello", language) == []

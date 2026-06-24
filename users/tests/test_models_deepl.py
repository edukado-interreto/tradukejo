import pytest
from django.core.exceptions import ValidationError
from model_bakery import baker

from users.models import DeeplAuthKey, deepl_api_key


def test_validation_deepl_api_key():
    assert deepl_api_key("a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6:fx") is None

    with pytest.raises(ValidationError):
        # Fails when no column
        deepl_api_key("abc")
    with pytest.raises(ValidationError):
        # Fails when length is wrong
        deepl_api_key("ab:cd")
    with pytest.raises(ValidationError):
        # Fails when no hyphens
        deepl_api_key("a" * 36 + ":fx")
    with pytest.raises(ValidationError):
        # Fails when too many hyphens
        deepl_api_key("11111-22222-33333-44444-55555-666666:fx")


def test_deepl_auth_key_str():
    auth_key = baker.prepare(DeeplAuthKey)
    first, last = auth_key.api_key[:4], auth_key.api_key[-4:]
    assert str(auth_key) == first + "******" + last


def test_deepl_auth_key_default():
    auth_key = baker.prepare(DeeplAuthKey)
    assert auth_key.name == ""
    assert auth_key.plan == "free"
    assert auth_key.character_count == 0
    assert auth_key.user is None


def test_deepl_auth_key_properties():
    auth_key = baker.prepare(DeeplAuthKey)
    assert auth_key.character_limit == 5 * 10**5

import json
from contextlib import contextmanager
from typing import Any
from django.conf import settings
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from users.models import DeeplAuthKey


def _fetch_deepl(auth_key, endpoint, data=None):
    url = f"{settings.DEEPL_URL}/{endpoint}"
    headers = {
        "Authorization": f"DeepL-Auth-Key {auth_key.api_key}",
        "Content-Type": "application/json",
    }

    if data:
        data = json.dumps(data).encode()

    try:
        return urlopen(Request(url, data, headers))
    except HTTPError as error:
        data = json.loads(error.read())
        print(f"[{error}]", data.get("message", data))
        return error


def update_deepl_usage(auth_key: DeeplAuthKey):
    response = _fetch_deepl(auth_key, "usage")
    if response.code != 200:
        print("Error getting DeepL API usage.")
        return

    data = json.loads(response.read())
    return auth_key.update_count(data["character_count"])


@contextmanager
def deepl_usage(auth_key: DeeplAuthKey):
    try:
        yield
    except Exception:
        raise
    finally:
        update_deepl_usage(auth_key)


def fetch_deepl(endpoint, data: dict[str, Any] | None = None):
    if (auth_key := DeeplAuthKey.get_least_used()) is None:
        print("No DeepL Auth key provided, skipping translation.")
        return

    with deepl_usage(auth_key):
        return _fetch_deepl(auth_key, endpoint, data)


def fetch_deepl_translate(project, text, language) -> dict[str, Any] | None:
    data = {
        "text": text if isinstance(text, list) else [text],
        "target_lang": language.code,
        "source_lang": project.source_language.code,
        "context": project.description,
    }

    response = fetch_deepl("translate", data)
    if not response or response.code != 200:
        return

    return json.loads(response.read())


def deepl_translate(project, text, language) -> list[str]:
    if (data := fetch_deepl_translate(project, text, language)) is None:
        return []

    # {"translations": [{"text": "vorto", "detected_source_language": "EN"},…]}
    return [tr["text"] for tr in data["translations"]]

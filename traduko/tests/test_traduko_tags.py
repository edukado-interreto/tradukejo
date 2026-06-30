from unittest.mock import patch

import pytest
from django.test import RequestFactory

from traduko.templatetags import traduko_tags as uut


def test_querystring():
    assert uut.querystring("a", "1", "b", "2") == "?a=1&b=2"
    assert uut.querystring("a", "1", "b", "") == "?a=1"


def test_number_range():
    assert list(uut.number_range(3)) == [0, 1, 2]


def test_dict_key_and_list_index():
    assert uut.dict_key({"x": "y"}, "x") == "y"
    assert uut.dict_key({"x": "y"}, "z") == ""
    assert uut.dict_key("", "x") == ""
    assert uut.list_index(["a", "b"], 1) == "b"
    assert uut.list_index(["a"], 3) == ""


def test_highlight_placeholders():
    assert uut.highlight_placeholders("Hello {name}") == "Hello <code>{name}</code>"
    assert uut.highlight_placeholders("Use %s here") == "Use <code>%s</code> here"
    assert "&lt;script&gt;" in uut.highlight_placeholders("<script>", escape=True)


def test_format_translation():
    html = uut.format_translation("Visit {1}site{/1}", "https://example.com")
    assert 'href="https://example.com"' in html
    assert 'target="_blank"' in html
    assert "site" in html


from tradukejo import settings


@pytest.mark.django_db
def test_user_link(admin_user):
    assert uut.user_link(None, None) == settings.WEBSITE_NAME
    link = uut.user_link(admin_user.pk, admin_user.username)
    assert admin_user.username in link
    assert f"/user/{admin_user.pk}/" in link


def test_get_language_name():
    assert uut.get_language_name("eo") == "Esperanto"
    assert uut.get_language_name("xx-unknown") == "xx-unknown"


@pytest.mark.django_db
def test_translate_abs_url():
    request = RequestFactory().get("/eo/project/1/")
    context = {"request": request}
    with patch(
        "traduko.templatetags.traduko_tags.urls.translate_url"
    ) as mock_translate:
        mock_translate.return_value = "/en/project/1/"
        assert uut.translate_abs_url(context, "en") == "/en/project/1/"
        mock_translate.assert_called_once()

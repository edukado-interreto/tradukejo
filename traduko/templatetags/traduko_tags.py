from typing import Optional, Any, Dict
from django import template
from django import urls
from django.utils import html
import re
from django.utils.safestring import mark_safe
from tradukejo import settings

register = template.Library()


@register.simple_tag
def querystring(*args):
    q = ""
    i = 0
    while i < len(args):
        if args[i + 1] != "":
            if q == "":
                q = "?"
            else:
                q = q + "&"
            q = q + args[i] + "=" + args[i + 1]
        i = i + 2
    return q


@register.filter(name="range")
def number_range(n):
    return range(n)


@register.filter(name="dict_key")
def dict_key(d, k):
    """Returns the given key from a dictionary."""
    if d == "":
        return ""
    elif k in d.keys():
        return d[k]
    else:
        return ""


@register.filter(name="list_index")
def list_index(l, i):
    """Returns the given element from a list."""
    l = list(l)
    if i < len(l):
        return l[i]
    else:
        return ""


@register.filter(name="highlight_placeholders")
def highlight_placeholders(str, escape=True):
    if escape:
        str = html.escape(str)
    str = re.sub(
        r"\{(([0-9a-zA-Z._:,=+^!/[\]-]|&lt;|&gt;)*)\}", r"<code>{\1}</code>", str
    )
    str = str.replace(
        "&#x27;", "'"
    )  # Unescaping single quotes but shouldn't be dangerous
    str = re.sub(r"(%[0-9a-zA-Z().-]*[a-zA-Z]|\'{2,3})", r"<code>\1</code>", str)

    return str


@register.simple_tag
def user_link(user_id, username):
    if not user_id or not username:
        return settings.WEBSITE_NAME
    else:
        link = urls.reverse("profile", args=[user_id])
        return html.format_html('<a href="{}">{}</a>', link, username)


@register.simple_tag
def format_translation(text, *args):
    text = html.escape(text)
    i = 1
    while i <= len(args):
        value = str(args[i - 1])
        target = (
            ' target="_blank"'
            if value.startswith("https://") or value.startswith("http://")
            else ""
        )
        text = re.sub(
            r"\{%d\}(.*)\{/%d\}" % (i, i),
            r'<a href="{%d}"%s>\1</a>' % (i, target),
            text,
        )
        text = text.replace("{%d}" % i, value)
        i += 1
    return mark_safe(text)


@register.simple_tag(takes_context=True)
def translate_url(context: Dict[str, Any], language: Optional[str]) -> str:
    """Get the absolute URL of the current page for the specified language.

    Usage:
        {% translate_url 'en' %}
    """
    print(context)
    url = context["request"].get_full_path()
    return urls.translate_url(url, language)


@register.simple_tag(takes_context=True)
def translate_abs_url(context: Dict[str, Any], language: Optional[str]) -> str:
    """Get the absolute URL of the current page for the specified language.

    Usage:
        {% translate_abs_url 'en' %}
    """
    url = context["request"].build_absolute_uri()
    return urls.translate_url(url, language)


@register.filter(name="get_language_name")
def get_language_name(str):
    for code, language in settings.LANGUAGES:
        if code == str:
            return language
    return str

from django import template
from django.utils import html
import re

from django.utils.html import format_html

from tradukejo import settings

register = template.Library()


@register.simple_tag
def querystring(*args):
    q = ''
    i = 0
    while i < len(args):
        if args[i+1] != "":
            if q == '':
                q = '?'
            else:
                q = q + '&'
            q = q + args[i] + '=' + args[i+1]
        i = i + 2
    return q


@register.filter(name="range")
def number_range(n):
    return range(n)


@register.filter(name='dict_key')
def dict_key(d, k):
    '''Returns the given key from a dictionary.'''
    if d == "":
        return ""
    elif k in d.keys():
        return d[k]
    else:
        return ""


@register.filter(name='list_index')
def list_index(l, i):
    '''Returns the given element from a list.'''
    l = list(l)
    if i < len(l):
        return l[i]
    else:
        return ""


@register.filter(name='highlight_placeholders')
def highlight_placeholders(str):
    str = html.escape(str)
    str = re.sub(
        r'\{(([0-9a-z._:,=+^!/[\]-]|&lt;|&gt;)*)\}',
        r'<code>{\1}</code>',
        str
    )
    str = re.sub(
        r'(%[a-z0-9.-]*[a-zA-Z])',
        r'<code>\1</code>',
        str
    )

    return str


@register.simple_tag
def user_link(user_id, username):
    if not user_id or not username:
        return settings.WEBSITE_NAME
    else:
        return format_html('<a href="#">{}</a>', username)

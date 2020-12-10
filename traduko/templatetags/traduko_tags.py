from django import template

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

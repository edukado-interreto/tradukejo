from urllib.parse import urlencode


def nested_urlencode(params):
    """
    Encode form data in PHP http_build_query style.

    >>> params = {"to": {"a@eg.tld": "", "b@eg.tld": {"vars": {"name": "b"}}}}
    >>> nested_urlencode(params)
    'to%5Ba%40eg.tld%5D=&to%5Bb%40eg.tld%5D%5Bvars%5D%5Bname%5D=b'
    >>> urllib.parse.unquote_plus(_)
    'to[a@eg.tld]=&to[b@eg.tld][vars][name]=b'

    Borrowed from: https://stackoverflow.com/a/43347067
    Ref: https://www.php.net/manual/en/function.http-build-query.php
    """
    ret = {}

    def _encode(params, param_key=None):
        _encoded_params = {}
        if isinstance(params, dict):
            for key, value in params.items():
                _encoded_params[f"{param_key}[{key}]"] = value
        elif isinstance(params, (list, tuple)):
            for index, value in enumerate(params):
                _encoded_params[f"{param_key}[{index}]"] = value
        else:
            ret[param_key] = params

        for key, value in _encoded_params.items():
            _encode(value, key)

    if isinstance(params, dict):
        for key, value in params.items():
            _encode(params=value, param_key=key)

    return urlencode(ret, doseq=True)

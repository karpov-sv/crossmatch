from __future__ import absolute_import, division, print_function, unicode_literals

from django.shortcuts import redirect

import urllib

def redirect_get(url_or_view, *args, **kwargs):
    get_params = kwargs.pop('get', None)

    response = redirect(url_or_view, *args, **kwargs)
    if get_params:
        response['Location'] += '?' + urllib.urlencode(get_params)

    return response

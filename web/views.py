from __future__ import absolute_import, division, print_function, unicode_literals

from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.views.decorators.cache import cache_page
from django.core.cache import cache

import datetime, re, urllib

from memoize import memoize

from resolve import resolve
from .utils import redirect_get

@memoize(timeout=3600)
def test(value):
    print('test3')
    return value*2

def index(request):
    context = {}

    return TemplateResponse(request, 'index.html', context=context)

def search(request, mode='cutouts'):

    context = {}

    return TemplateResponse(request, 'index.html', context=context)

from __future__ import absolute_import, division, print_function, unicode_literals

from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.views.decorators.cache import cache_page
from django.core.cache import cache

import datetime, re, urllib
import numpy as np
from astropy.table import Column

from memoize import memoize

from resolve import resolve
from cats import get_cat, catslist

@memoize(timeout=3600*24)
def get_cat_cached(catname, ra, dec, sr):
    return get_cat(catname, ra=ra, dec=dec, sr=sr, dirname=None, self_match=False)

@memoize(timeout=3600*24)
def get_cats_cached(catnames, ra, dec, sr):
    cats = []

    for _ in catnames:
        cat = get_cat_cached(_, ra, dec, np.hypot(sr, catslist[_]['sr']/3600))

        if cat:
            cats.append(cat);

    return cats

@memoize(timeout=3600*24)
def sed_worker(ra, dec, sr):
    log = []

    print("sed_worker")

    catnames = ['denis', 'gaiadr2', 'galex', 'iphas', 'lamost', 'ps1', 'sdss', 'ukidss', 'wise', 'tycho2', 'skymapper']
    cats = get_cats_cached(catnames, ra=ra, dec=dec, sr=sr)

    return {'cats': cats, 'log': log}

def sed(request):
    context = {'sr': 1/3600, 'log': []}

    if request.method == 'POST':
        # Form submission handling

        coords = request.POST.get('coords')
        sr = 1/3600
        name,ra,dec = resolve(coords)

        for _ in ['coords', 'preview']:
            context[_] = request.POST.get(_)

        if not name:
            context['message'] = "Can't resolve position: " + coords
        else:
            context['name'] = name
            context['ra'] = ra
            context['dec'] = dec
            context['sr'] = sr

            work = sed_worker(ra, dec, sr)

            context['cats'] = work['cats']

            context['log'] = work['log']

    return TemplateResponse(request, 'sed.html', context=context)

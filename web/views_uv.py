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
from match import match

@memoize(timeout=3600*24)
def get_cat_cached(catname, ra, dec, sr):
    return get_cat(catname, ra=ra, dec=dec, sr=sr, dirname=None)

@memoize(timeout=3600*24)
def get_cats_cached(catnames, ra, dec, sr):
    cats = []

    for _ in catnames:
        cat = get_cat_cached(_, ra, dec, sr)

        if cat:
            cats.append(cat);

    return cats

@memoize(timeout=3600*24)
def uv_only_worker(ra, dec, sr):
    log = []

    print("uv_only_worker")

    catnames = ['galex', 'gaiadr2', 'ps1', 'wise', 'sdss', 'ukidss', 'denis']
    cats = get_cats_cached(catnames, ra=ra, dec=dec, sr=sr)

    if cats[0]['name'] == 'galex':
        galex = cats[0]
        ids = np.arange(len(galex['table']))
        idx = np.zeros_like(ids, dtype=np.bool)
        galex['table'].add_column(Column(data=np.zeros(len(galex['table']), dtype=np.int64), name='nmatches'))

        log.append('%d GALEX objects in the field' % len(ids))

        for cat in cats[1:]:
            m = match(galex, cat)
            idx1 = np.isin(ids, m[0])
            idx |= idx1

            galex['table'].add_column(Column(data=np.zeros(len(galex['table']), dtype=np.int64), name='match_' + cat['name']))
            galex['table']['match_' + cat['name']][idx1] += 1
            galex['table']['nmatches'][idx1] += 1

            log.append('Matching with %s: %d matched' % (cat['name'], np.sum(idx1)))

        nidx = ~idx
        log.append('%d matched in total' % sum(idx))
        log.append('%d GALEX objects not matched' % sum(nidx))
    else:
        galex = None
        idx = None
        nidx = None
        log.append('No GALEX objects in the field')

    return {'cats': cats, 'log': log, 'galex': galex, 'idx': idx, 'nidx': nidx}

def uv_only(request, size=512):
    context = {'sr': 0.1, 'log': []}

    if request.method == 'POST':
        # Form submission handling

        coords = request.POST.get('coords')
        sr = float(request.POST.get('sr', 0.1))
        name,ra,dec = resolve(coords)

        for _ in ['coords', 'preview', 'nuv', 'fuv']:
            context[_] = request.POST.get(_)

        if not name:
            context['message'] = "Can't resolve position: " + coords
        else:
            context['name'] = name
            context['ra'] = ra
            context['dec'] = dec
            context['sr'] = float(sr) if sr else 0.1

            work = uv_only_worker(ra, dec, sr)

            context['cats'] = work['cats']

            if work['galex']:
                table = work['galex']['table']
                table = table[work['nidx']]

                if request.POST.get('nuv'):
                    table = table[table['NUV'] < float(request.POST.get('nuv'))]

                if request.POST.get('fuv'):
                    table = table[table['FUV'] < float(request.POST.get('fuv'))]

                context['table'] = table

                context['has_sdss'] = 'sdss' in [_['name'] for _ in work['cats']]

            context['log'] = work['log']

    return TemplateResponse(request, 'uv-only.html', context=context)

def uv_only_download(request):
    ra,dec,sr = [float(request.GET.get(_)) for _ in ['ra', 'dec', 'sr']]

    work = uv_only_worker(ra, dec, sr)

    response = HttpResponse(request, content_type='application/x-votable+xml')
    response['Content-Disposition'] = 'attachment; filename=%s_%s_%s_%s.xml' % ('galex', ra, dec, sr)

    work['galex']['table'].write(response, format='votable')

    return response

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

def uv_only_plot(request):
    ra,dec,sr = [float(request.GET.get(_)) for _ in ['ra', 'dec', 'sr']]
    field = request.GET.get('field')
    width = 600

    work = uv_only_worker(ra, dec, sr)
    value = work['galex']['table'][field]
    nidx = work['nidx']

    fig = Figure(facecolor='white', figsize=(width/72, width*0.5/72), dpi=72, tight_layout=True)
    ax = fig.add_subplot(111)

    ax.hist(value, bins=np.arange(15, 25, 0.5), alpha=0.5, label='All');
    ax.hist(value[nidx], bins=np.arange(15, 25, 0.5), alpha=0.5, label='Not matched');
    ax.set_xlabel(field)
    ax.set_title('ra=%s dec=%s sr=%s' % (ra, dec, sr))
    ax.legend()

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/jpeg')
    canvas.print_jpg(response)

    return response

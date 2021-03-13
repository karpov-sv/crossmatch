from __future__ import absolute_import, division, print_function, unicode_literals

from django.template.response import TemplateResponse
from django.core.cache import cache
from django.urls import reverse
from django.shortcuts import redirect

from collections import OrderedDict

import urllib
from . import ps1

from resolve import resolve

def cutouts_ps1(request, size=512):
    ra, dec, sr, size = request.GET.get('ra'), request.GET.get('dec'), request.GET.get('sr', 0.1), request.GET.get('size', 512)
    cid = 'cutout_ps1_%s_%s_%s_%s' % (ra, dec, sr, size)
    url = cache.get(cid)

    if url is None:
        print('cutout_ps1')
        url = ps1.geturl(request.GET.get('ra'), request.GET.get('dec'), size=int(float(request.GET.get('sr'))*3600/0.25), output_size=request.GET.get('size', 512), color=True)
        cache.set(cid, url, 3600)

    return redirect(url)

# cutouts_direct = ['galex_nuv', 'galex_fuv', 'dss', 'sdss']

surveys = OrderedDict([
    ['galex', {'name': 'GALEX', 'hips': 'CDS/P/GALEXGR6/AIS/color', 'default':True}],

    ['galex_nuv', {'name': 'GALEX NUV'}],
    ['galex_fuv', {'name': 'GALEX FUV'}],

    ['dss2', {'name': 'DSS2', 'hips': 'DSS2/color', 'default':True}],
    # ['dss2b', {'name': 'DSS2 blue', 'hips': 'DSS2/blue'}],
    # ['dss2r', {'name': 'DSS2 blue', 'hips': 'DSS2/blue'}],

    ['sdss', {'name': 'SDSS DR12', 'default':True}],

    ['panstarrs', {'name': 'PanSTARRS', 'hips': 'CDS/P/PanSTARRS/DR1/color', 'default':True}],

    ['skymapper', {'name': 'SkyMapper', 'hips': 'CDS/P/skymapper-color', 'default':True}],

    ['iphas_halpha', {'name': 'IPHAS Halpha', 'hips': 'CDS/P/IPHAS/DR2/halpha'}],
    ['vtss_halpha', {'name': 'VTSS Halpha', 'hips': 'CDS/P/VTSS/Ha'}],
    ['shassa_halpha', {'name': 'SHASSA Halpha', 'hips': 'CDS/P/SHASSA/H'}],
    ['shs_halpha', {'name': 'SHS Halpha', 'hips': 'CDS/P/SHS'}],

    ['wise', {'name': 'allWISE', 'hips': 'CDS/P/allWISE/color', 'default':True}],
    ['wise_w1', {'name': 'WISE 3.4um', 'hips': 'CDS/P/allWISE/W1'}],
    ['wise_w2', {'name': 'WISE 4.6um', 'hips': 'CDS/P/allWISE/W2'}],
    ['wise_w3', {'name': 'WISE 12um', 'hips': 'CDS/P/allWISE/W3'}],
    ['wise_w4', {'name': 'WISE 22um', 'hips': 'CDS/P/allWISE/W4'}],

    ['glimpse360', {'name': 'GLIMPSE360', 'hips': 'IPAC/P/GLIMPSE360'}],

])

def get_cutout_url(survey, ra, dec, sr, size, overlay=False):
    # generic HIPS
    if surveys.has_key(survey) and surveys[survey].has_key('hips'):
        return {'name': surveys[survey]['name'],
                'url': 'http://alasky.u-strasbg.fr/hips-image-services/hips2fits?' + urllib.urlencode({
                    'hips': surveys[survey]['hips'],
                    'ra': ra,
                    'dec': dec,
                    'width': size,
                    'height': size,
                    'fov': sr,
                    'projection': 'TAN',
                    'coordsys': 'icrs',
                    'rotation_angle': 0.0,
                    'format': 'jpg',
                    'stretch': 'linear',
                    'cmap': 'viridis'}),
                'fits': 'http://alasky.u-strasbg.fr/hips-image-services/hips2fits?' + urllib.urlencode({
                    'hips': surveys[survey]['hips'],
                    'ra': ra,
                    'dec': dec,
                    'width': size,
                    'height': size,
                    'fov': sr,
                    'projection': 'TAN',
                    'coordsys': 'icrs',
                    'rotation_angle': 0.0,
                    'format': 'fits'})
                }

    # GALEX
    elif survey == 'galex_nuv':
        return {'name': 'GALEX NUV',
                'url': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urllib.urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'galex near uv',
                    'Catalog': 'II/335/galex_ais' if overlay else None,
                    'Return': 'GIF',
                    'LUT': 'colortables/blue-white.bin'}),
                'fits': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urllib.urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'galex near uv',
                    'Return': 'FITS'})}
    elif survey == 'galex_fuv':
        return {'name': 'GALEX FUV',
                'url': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urllib.urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'galex far uv',
                    'Catalog': 'II/335/galex_ais' if overlay else None,
                    'Return': 'GIF',
                    'LUT': 'colortables/blue-white.bin'}),
                'fits': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urllib.urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'galex far uv',
                    'Return': 'FITS'})}
    # DSS
    elif survey == 'dss':
        return {'name': 'DSS',
                'url': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urllib.urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'DSS',
                    'Catalog': 'I/345/gaia2' if overlay else None, # Gaia
                    'Return': 'GIF',
                    'LUT': 'colortables/blue-white.bin'})}

    # SDSS
    elif survey == 'sdss':
        return {'name': 'SDSS DR12',
                'url': 'http://skyserver.sdss.org/dr12/SkyserverWS/ImgCutout/getjpeg?' + urllib.urlencode({
                    'ra': ra,
                    'dec': dec,
                    'width': size,
                    'height': size,
                    'scale': sr*3600/size,
                    'opt': 'PI' if overlay else ''})}

    # PS1
    elif survey == 'ps1orig':
        return {'name': 'PanSTARRS',
                'url': reverse('cutouts_ps1') + '?' + urllib.urlencode({
                    'ra': ra,
                    'dec': dec,
                    'sr': sr,
                    'size': size})}


    return None

def cutouts(request, size=512):
    context = {'sr_value': 0.1, 'sr_units': 'deg'}

    context['selected'] = [_ for _ in surveys.keys() if surveys[_].get('default')]
    context['surveys'] = surveys

    if request.method == 'POST' or request.GET.get('coords'):
        # Form submission handling

        for _ in ['coords', 'multicoords', 'sr_value', 'sr_units', 'sr']:
            context[_] = request.POST.get(_, request.GET.get(_))

        if context['sr']:
            context['sr_value'] = context['sr']
            context['sr_units'] = 'deg'
        else:
            context['sr'] = float(context['sr_value']) if context['sr_value'] else 0.01
            if context['sr_units'] == 'arcmin':
                context['sr'] /= 60
            elif context['sr_units'] == 'arcsec':
                context['sr'] /= 3600

        if request.POST.get('selected'):
            context['selected'] = request.POST.getlist('selected')

        coords = request.POST.get('coords', request.GET.get('coords'))
        multicoords = request.POST.get('multicoords')

        if multicoords:
            multicoords = multicoords.splitlines()

        targets = []

        clist = []
        if coords:
            clist += [coords]
        if multicoords:
            clist += multicoords

        for coord in clist:
            if not coord:
                continue

            target = {}

            name,ra,dec = resolve(coord)

            if not name:
                target['message'] = "Can't resolve position: " + coord
            else:
                target['name'] = name
                target['ra'] = ra
                target['dec'] = dec

                target['cutouts'] = OrderedDict()

                for _ in surveys.keys():
                    if _ in context['selected']:
                        cut = get_cutout_url(_, ra, dec, context['sr'], size)
                        if cut is not None:
                            target['cutouts'][_] = cut

            targets.append(target)

        context['targets'] = targets

        nselected = len(context['selected'])

        if nselected < 4:
            context['colsize'] = 4
        elif nselected == 4:
            context['colsize'] = 3
        else:
            context['colsize'] = 2

    return TemplateResponse(request, 'cutouts.html', context=context)

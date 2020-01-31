from __future__ import absolute_import, division, print_function, unicode_literals

from django.template.response import TemplateResponse
from django.core.cache import cache
from django.urls import reverse
from django.shortcuts import redirect

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

cutout_surveys = ['galex_nuv', 'galex_fuv', 'dss', 'sdss', 'ps1', 'wise_w1', 'wise_w2', 'wise_w3', 'wise_w4']

def get_cutout_url(survey, ra, dec, sr, size):
    # GALEX
    if survey == 'galex_nuv':
        return {'name': 'GALEX NUV',
                'url': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urllib.urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'galex near uv',
                    'Catalog': 'II/335/galex_ais',
                    'Return': 'GIF',
                    'LUT': 'colortables/blue-white.bin'})}
    elif survey == 'galex_fuv':
        return {'name': 'GALEX FUV',
                'url': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urllib.urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'galex far uv',
                    'Catalog': 'II/335/galex_ais',
                    'Return': 'GIF',
                    'LUT': 'colortables/blue-white.bin'})}

    # DSS
    elif survey == 'dss':
        return {'name': 'DSS',
                'url': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urllib.urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'DSS',
                    'Catalog': 'I/345/gaia2', # Gaia
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
                    'opt': 'PI'})}

    # PS1
    elif survey == 'ps1':
        return {'name': 'PanSTARRS',
                'url': reverse('cutouts_ps1') + '?' + urllib.urlencode({
                    'ra': ra,
                    'dec': dec,
                    'sr': sr,
                    'size': size})}

    # WISE
    elif survey == 'wise_w1':
        return {'name': 'WISE 3.4um',
                'url': 'http://alasky.u-strasbg.fr/hips-image-services/hips2fits?' + urllib.urlencode({
                    'hips': 'CDS/P/allWISE/W1',
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
                    'cmap': 'viridis'})}
    elif survey == 'wise_w2':
        return {'name': 'WISE 4.6um',
                'url': 'http://alasky.u-strasbg.fr/hips-image-services/hips2fits?' + urllib.urlencode({
                    'hips': 'CDS/P/allWISE/W2',
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
                    'cmap': 'viridis'})}
    elif survey == 'wise_w3':
        return {'name': 'WISE 12um',
                'url': 'http://alasky.u-strasbg.fr/hips-image-services/hips2fits?' + urllib.urlencode({
                    'hips': 'CDS/P/allWISE/W3',
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
                    'cmap': 'viridis'})}
    elif survey == 'wise_w4':
        return {'name': 'WISE 22um',
                'url': 'http://alasky.u-strasbg.fr/hips-image-services/hips2fits?' + urllib.urlencode({
                    'hips': 'CDS/P/allWISE/W4',
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
                    'cmap': 'viridis'})}

    return None

def cutouts(request, size=512):
    context = {'sr': 0.01}

    if request.method == 'POST' or request.GET.get('coords'):
        # Form submission handling

        coords = request.POST.get('coords', request.GET.get('coords'))
        sr = float(request.POST.get('sr', request.GET.get('sr', 0.1)))

        name,ra,dec = resolve(coords)

        for _ in ['coords']:
            context[_] = request.POST.get(_, request.GET.get(_))

        if not name:
            context['message'] = "Can't resolve position: " + coords
        else:
            context['name'] = name
            context['ra'] = ra
            context['dec'] = dec
            context['sr'] = float(sr) if sr else 0.1

            context['cutouts'] = []

            for _ in cutout_surveys:
                cut = get_cutout_url(_, ra, dec, sr, size)
                if cut is not None:
                    context['cutouts'].append(cut)

    return TemplateResponse(request, 'cutouts.html', context=context)

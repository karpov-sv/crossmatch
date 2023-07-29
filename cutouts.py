from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import posixpath, glob, datetime, os, sys, urllib, shutil, itertools

try:
    from urllib import urlencode # Python 2
except:
    from urllib.parse import urlencode # Python 3

from collections import OrderedDict

surveys = OrderedDict([
    ['galex', {'name': 'GALEX', 'hips': 'CDS/P/GALEXGR6/AIS/color', 'default':True}],

    ['galex_nuv', {'name': 'GALEX NUV'}],
    ['galex_fuv', {'name': 'GALEX FUV'}],

    ['dss2', {'name': 'DSS2', 'hips': 'DSS2/color', 'default':True}],
    # ['dss2b', {'name': 'DSS2 blue', 'hips': 'DSS2/blue'}],
    # ['dss2r', {'name': 'DSS2 blue', 'hips': 'DSS2/blue'}],

    ['sdss', {'name': 'SDSS DR12', 'default':True}],

    ['panstarrs', {'name': 'PanSTARRS', 'hips': 'CDS/P/PanSTARRS/DR1/color', 'default':True}],
    ['panstarrs_g', {'name': 'PanSTARRS', 'hips': 'CDS/P/PanSTARRS/DR1/g'}],
    ['panstarrs_r', {'name': 'PanSTARRS', 'hips': 'CDS/P/PanSTARRS/DR1/r'}],

    ['skymapper', {'name': 'SkyMapper', 'hips': 'CDS/P/skymapper-color', 'default':True}],
    ['skymapper_g', {'name': 'SkyMapper', 'hips': 'CDS/P/skymapper-g'}],
    ['skymapper_r', {'name': 'SkyMapper', 'hips': 'CDS/P/skymapper-r'}],

    ['des', {'name': 'Dark Energy Survey', 'hips': 'CDS/P/DES-DR1/color'}],
    ['des_g', {'name': 'Dark Energy Survey', 'hips': 'CDS/P/DES-DR1/g'}],
    ['des_r', {'name': 'Dark Energy Survey', 'hips': 'CDS/P/DES-DR1/r'}],

    ['tess', {'name': 'TESS', 'hips': 'CDS/P/TESS/2yr'}],

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

    ['viking', {'name': 'VIKING', 'hips': 'CDS/P/VISTA/VIKING/color'}],
    ['viking_j', {'name': 'VIKING', 'hips': 'CDS/P/VISTA/VIKING/J'}],
    ['viking_h', {'name': 'VIKING', 'hips': 'CDS/P/VISTA/VIKING/H'}],
    ['viking_k', {'name': 'VIKING', 'hips': 'CDS/P/VISTA/VIKING/H'}],
    ['viking_y', {'name': 'VIKING', 'hips': 'CDS/P/VISTA/VIKING/Y'}],
    ['viking_z', {'name': 'VIKING', 'hips': 'CDS/P/VISTA/VIKING/Z'}],

    ['kids_g', {'name': 'KiDS', 'hips': 'CDS/P/KiDS/DR5/color-ug'}],
    ['kids_r', {'name': 'KiDS', 'hips': 'CDS/P/KiDS/DR5/color-gri'}],
])

def get_cutout_url(survey, ra, dec, sr, size, overlay=False):
    if overlay is True:
        if 'galex' in survey:
            overlay = 'II/335/galex_ais' # Galex
        else:
            overlay = 'I/345/gaia2' # Gaia

    # generic HIPS
    if survey in surveys and 'hips' in surveys[survey]:
        return {'name': surveys[survey]['name'],
                'url': 'http://alasky.u-strasbg.fr/hips-image-services/hips2fits?' + urlencode({
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
                    'stretch': 'asinh',
                    'cmap': 'viridis'}),
                'fits': 'http://alasky.u-strasbg.fr/hips-image-services/hips2fits?' + urlencode({
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
                'url': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'galex near uv',
                    'Catalog': overlay if overlay else None,
                    'Return': 'GIF',
                    'scaling': 'histeq',
                    # 'PlotColor': 'red',
                    'PlotScale': 5,
                    'LUT': 'colortables/blue-white.bin'}),
                'fits': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'galex near uv',
                    'Return': 'FITS'})}
    elif survey == 'galex_fuv':
        return {'name': 'GALEX FUV',
                'url': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'galex far uv',
                    'Catalog': overlay if overlay else None,
                    'Return': 'GIF',
                    'scaling': 'histeq',
                    # 'PlotColor': 'red',
                    'PlotScale': 5,
                    'LUT': 'colortables/blue-white.bin'}),
                'fits': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'galex far uv',
                    'Return': 'FITS'})}
    # DSS
    elif survey == 'dss':
        return {'name': 'DSS',
                'url': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'DSS',
                    'Catalog': overlay if overlay else None, # Gaia
                    'Return': 'GIF',
                    'scaling': 'histeq',
                    'PlotColor': 'red',
                    'PlotScale': 5,
                    'LUT': 'colortables/blue-white.bin'})}

    elif survey == 'dss2_blue':
        return {'name': 'DSS',
                'url': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'DSS2 Blue',
                    'Catalog': overlay if overlay else None, # Gaia
                    'Return': 'GIF',
                    'scaling': 'histeq',
                    'PlotColor': 'red',
                    'PlotScale': 5,
                    'LUT': 'colortables/blue-white.bin'})}

    elif survey == 'dss2_red':
        return {'name': 'DSS',
                'url': 'https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?' + urlencode({
                    'Position': '%s,%s' % (ra, dec),
                    'Size': sr,
                    'Pixels': size,
                    'Survey': 'DSS2 Red',
                    'Catalog': overlay if overlay else None, # Gaia
                    'Return': 'GIF',
                    'scaling': 'histeq',
                    'PlotColor': 'red',
                    'PlotScale': 5,
                    'LUT': 'colortables/blue-white.bin'})}

    # SDSS
    elif survey == 'sdss':
        return {'name': 'SDSS DR12',
                'url': 'http://skyserver.sdss.org/dr12/SkyserverWS/ImgCutout/getjpeg?' + urlencode({
                    'ra': ra,
                    'dec': dec,
                    'width': size,
                    'height': size,
                    'scale': sr*3600/size,
                    'opt': 'PI' if overlay else ''})}

    # # PS1
    # elif survey == 'ps1orig':
    #     return {'name': 'PanSTARRS',
    #             'url': reverse('cutouts_ps1') + '?' + urlencode({
    #                 'ra': ra,
    #                 'dec': dec,
    #                 'sr': sr,
    #                 'size': size})}


    return None

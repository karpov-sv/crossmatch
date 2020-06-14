from __future__ import absolute_import, division, print_function, unicode_literals

from django import template
from django.utils.safestring import mark_safe

from astropy.coordinates import SkyCoord

from .. import views_cutouts

register = template.Library()

@register.simple_tag(takes_context=False)
def cutout(survey, ra, dec, sr, size=512):
    return views_cutouts.get_cutout_url(survey, ra, dec, sr, size)['url']

@register.simple_tag(takes_context=False)
def cutout_img(survey, ra, dec, sr, size=512):
    cutout = views_cutouts.get_cutout_url(survey, ra, dec, sr, size)

    return mark_safe('<img src="%s" class="img-fluid img-thumbnail" title="%s">' % (cutout['url'], cutout['name']))

@register.simple_tag(takes_context=False)
def cat_row_ra(cat, row):
    return row[cat.get('ra', 'RAJ2000')]

@register.simple_tag(takes_context=False)
def cat_row_dec(cat, row):
    return row[cat.get('dec', 'DEJ2000')]

@register.simple_tag(takes_context=False)
def galactic_l(ra, dec):
    c = SkyCoord(ra, dec, unit='deg', frame='icrs')
    return c.transform_to('galactic').l.to_string(decimal=True)

@register.simple_tag(takes_context=False)
def galactic_b(ra, dec):
    c = SkyCoord(ra, dec, unit='deg', frame='icrs')
    return c.transform_to('galactic').b.to_string(decimal=True, alwayssign=True)

@register.simple_tag(takes_context=False)
def eq_ra(ra, dec):
    c = SkyCoord(ra, dec, unit='deg', frame='icrs')
    return c.ra.to_string(unit='hour', sep=' ', pad=True)

@register.simple_tag(takes_context=False)
def eq_dec(ra, dec):
    c = SkyCoord(ra, dec, unit='deg', frame='icrs')
    return c.dec.to_string(sep=' ', pad=True, alwayssign=True)

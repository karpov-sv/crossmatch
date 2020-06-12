from __future__ import absolute_import, division, print_function, unicode_literals

from django import template
from django.utils.safestring import mark_safe

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

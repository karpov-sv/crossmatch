from __future__ import absolute_import, division, print_function, unicode_literals

from django import template
register = template.Library()

from django.utils.safestring import mark_safe

@register.filter
def cat_get(value, name):
    if name == 'ra':
        return value.get('ra', 'RAJ2000')
    if name == 'dec':
        return value.get('ra', 'DEJ2000')

    return value.get(name)

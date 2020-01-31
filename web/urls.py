from __future__ import absolute_import, division, print_function, unicode_literals

from django.http import HttpResponse
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import include, url

from . import settings

from . import views
from . import views_cutouts
from . import views_uv

urlpatterns = [
    # Index
    url(r'^$', views.index, name="index"),

    url(r'search$', views.search, name="search"),
    url(r'cutouts$', views_cutouts.cutouts, name="cutouts"),
    url(r'cutouts/ps1$', views_cutouts.cutouts_ps1, name="cutouts_ps1"),

    url(r'uv-only$', views_uv.uv_only, name="uv-only"),
    url(r'uv-only/download$', views_uv.uv_only_download, name="uv-only_download"),
    url(r'uv-only/plot$', views_uv.uv_only_plot, name="uv-only_plot"),

    # Robots
    url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /\n", content_type="text/plain")),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

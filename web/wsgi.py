"""
WSGI config for web project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import posixpath

web_path = posixpath.split(os.path.abspath(__file__))[0]
web_uppath = posixpath.abspath(posixpath.join(web_path, '..'))

sys.path.append(web_path)
sys.path.append(web_uppath)

os.chdir(web_uppath)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)

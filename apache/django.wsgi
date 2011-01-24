import os
import sys

sys.path.append('/home/dhu/code')
sys.path.append('/home/dhu/code/rssfilter')

os.environ['DJANGO_SETTINGS_MODULE'] = 'rssfilter.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

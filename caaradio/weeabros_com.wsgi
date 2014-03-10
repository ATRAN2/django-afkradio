import os
import sys
sys.path.append('/var/www/weeabros.com/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'caaradio.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

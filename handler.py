from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healing.settings')

application = get_wsgi_application()

def handler(environ, start_response):
    from django.core.handlers.wsgi import WSGIHandler
    return WSGIHandler()(environ, start_response)

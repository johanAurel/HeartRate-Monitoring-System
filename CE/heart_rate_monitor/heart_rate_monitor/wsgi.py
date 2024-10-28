import os
from django.core.wsgi import get_wsgi_application

# Set the default settings module for the 'django' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heart_rate_monitor.settings')

# Get the WSGI application for the project.
application = get_wsgi_application()

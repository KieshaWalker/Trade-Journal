# api/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

# Ensure settings module is set for Vercel environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'walk.settings')
application = get_wsgi_application()
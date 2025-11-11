import os
from django.core.asgi import get_asgi_application

# Ensure settings module is set for Vercel environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'walk.settings')

application = get_asgi_application()

# Vercel's Python runtime will use the ASGI application. Expose both names.
app = application

# api/settings.py
ALLOWED_HOSTS = ['127.0.0.1', '.vercel.app']
# api/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'main_app',
]
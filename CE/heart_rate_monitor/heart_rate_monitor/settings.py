import os
from pathlib import Path
import secrets

def generate_django_secret_key():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(50))

key = generate_django_secret_key()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = key
DEBUG = True
ALLOWED_HOSTS = ['localhost']  # Fixed typo: 'locahost' to 'localhost'
AUTH_USER_MODEL = 'myapp.MyCustomUser'  # Ensure this is correctly defined

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',  # Your application
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs and WSGI
ROOT_URLCONF = 'heart_rate_monitor.urls'
WSGI_APPLICATION = 'heart_rate_monitor.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'heartbeat_monitor',  # Your database name
        'USER': 'postgres',           # PostgreSQL username
        'PASSWORD': 'postgres',       # PostgreSQL password
        'HOST': 'localhost',          # Use 'localhost' or your actual database host
        'PORT': '5432',               # Default PostgreSQL port
    }
}

# Authentication
AUTH_USER_MODEL = 'myapp.MyCustomUser'

# Custom user model
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # default backend
    'heart_rate_monitor.auth_backend.CustomUserBackend',  # your custom backend
]

# Primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Static files
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'


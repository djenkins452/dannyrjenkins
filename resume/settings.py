import os
from pathlib import Path

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!yonxx)qol3=3ef0l4lkpmsz(edd9s141ig)+-*=4)bj%9#pl_'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG=True forces ManifestStaticFilesStorage to return UNHASHED URLs
# (Django's _url() short-circuits the hash lookup when DEBUG is on),
# which defeats cache-busting on every CSS/JS change. Default to False
# so production gets hashed URLs automatically. Set DJANGO_DEBUG=true
# in your local shell to enable debug mode for local development.
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() in ('1', 'true', 'yes')

ALLOWED_HOSTS = [
    'dannyrjenkins.com',
    'www.dannyrjenkins.com',
    'beacon-innovation.com',
    'www.beacon-innovation.com',
    'django-resume-production-6ada.up.railway.app',
    'localhost',
    '127.0.0.1',
]

# CSRF: trusted origins must include scheme. Django 4+ requires this for any
# domain that submits POST requests (e.g. /admin/login/). Without these, the
# admin login returns 403 "CSRF verification failed — Origin checking failed".
CSRF_TRUSTED_ORIGINS = [
    'https://dannyrjenkins.com',
    'https://www.dannyrjenkins.com',
    'https://beacon-innovation.com',
    'https://www.beacon-innovation.com',
    'https://django-resume-production-6ada.up.railway.app',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tinymce',
    'website',
    'whitenoise.runserver_nostatic',

]

# TinyMCE: restricted toolbar — paragraphs, bold/italic, lists, links only.
# No font changes, colors, sizing, or headings (headings are controlled by
# structured model fields, not the editor). valid_elements enforces this
# server-side even if the browser bypasses the toolbar restrictions.
TINYMCE_DEFAULT_CONFIG = {
    'menubar': False,
    'statusbar': False,
    'branding': False,
    'height': 340,
    'plugins': 'link lists',
    'toolbar': 'bold italic | bullist numlist | link | undo redo',
    'valid_elements': 'p,br,strong,em,b,i,ul,ol,li,a[href|title|target|rel]',
    'extended_valid_elements': 'a[href|title|target|rel]',
    'forced_root_block': 'p',
    'content_style': (
        'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", '
        'Helvetica, Arial, sans-serif; font-size: 15px; line-height: 1.6; '
        'color: #111; max-width: 72ch; }'
    ),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'resume.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'website.context_processors.site',
            ],
        },
    },
]

WSGI_APPLICATION = 'resume.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Database: use DATABASE_URL (Railway Postgres) when set, otherwise fall back
# to local SQLite for development. dj-database-url parses DATABASE_URL from
# the environment and produces the correct DATABASES dict.
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        ssl_require=False,
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = ['static/']

#push site online
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -----------------------------------------------------------------------------
# Email — Private Email (Namecheap) SMTP over SSL on 465.
# Credentials come from Railway env vars (EMAIL_HOST_USER / _PASSWORD).
# Locally without those set, falls back to the console backend so form
# submissions print to stdout instead of failing at SMTP auth.
# -----------------------------------------------------------------------------
EMAIL_HOST = 'mail.privateemail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or 'webmaster@localhost'

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Baseline logging so email sends/failures surface in Railway deploy logs.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '[{levelname}] {name}: {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'},
    },
    'loggers': {
        'website': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}

"""
Django settings for washer_project project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import datetime
import os
from decimal import Decimal

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5oye%kl&wmh81y$p#4_rc!yb=0m&y76unw=fq(vufvdow&3dl3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_filters',
    'rest_framework',
    'rest_framework_swagger',
    'users',
    'address',
    'stores',
    'cars',
    'products',
    'baskets',
    'reservations'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'washer_project.urls'

WSGI_APPLICATION = 'washer_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'washer',
        'USER': 'postgres',
        'PORT': 5432,
    }
}

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.WasherPageNumberPagination',
    'ORDERING_PARAM': 'sort',
    'PAGINATE_BY': 20,
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'EXCEPTION_HANDLER': 'api.exceptions.exception_handler',
}

JWT_AUTH = {
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=365),
    'JWT_AUTH_HEADER_PREFIX': 'Token',
    'JWT_PAYLOAD_HANDLER': 'users.utils.jwt_payload_handler',
}


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
            ],
        },
    },
]

SWAGGER_SETTINGS = {
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'patch', 'put', 'options'],
}

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'tr-tr'

LANGUAGES = [
  ('tr-tr', 'Turkish'),
]

TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

AUTH_USER_MODEL = 'users.User'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

IMAGE_SIZES = {
    # To get the full size "full"
    "100x100":{
        "height": 100,
        "width": 100,
    },
    "250x250":{
        "height": 250,
        "width": 250,
    },
}

DEFAULT_PRODUCT_PRICE = Decimal('30.00')
MINIMUM_PRODUCT_PRICE = Decimal('0.99')


try:
    from washer_project.settings_local import *
except ImportError:
    pass

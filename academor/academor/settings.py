from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv('')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
#

##
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    "academor.az",
    "www.academor.az",
]

CSRF_TRUSTED_ORIGINS = [
    "https://www.academor.az",
    'https://academor.az',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
 
]

# CSRF Cookie Settings
CSRF_COOKIE_SECURE = True  
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

# Session Cookie Settings
SESSION_COOKIE_SECURE = True  
SESSION_COOKIE_HTTPONLY = True


# Admin URL - secret path (required)
ADMIN_URL = os.getenv('ADMIN_URL')
if not ADMIN_URL:
    raise ValueError("ADMIN_URL environment variable is required!")
if not ADMIN_URL.endswith('/'):
    ADMIN_URL += '/'
    

# # E-mail
# EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
# EMAIL_HOST = os.getenv('EMAIL_HOST')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
# EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
# SERVER_EMAIL = os.getenv('SERVER_EMAIL')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    # Third Packages
    'django_cleanup.apps.CleanupConfig',
    'ckeditor',
    
    # Apps
    'projects'
]

SITE_ID = 1

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'academor.middleware.CustomLocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'academor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'projects.context_processors.site_footer_context',
                'projects.context_processors.site_seo_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'academor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

# Public site default UI language
LANGUAGE_CODE = 'az'

# Django admin stays English (see academor.middleware.CustomLocaleMiddleware)
ADMIN_LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('az', 'Azərbaycan'),
    ('en', 'English'),
    ('ru', 'Русский'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Asia/Baku'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Media / Static configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Static files directories (only paths that exist — avoids staticfiles.W004 in Docker)
_candidate_static_dirs = (BASE_DIR / 'static', BASE_DIR / 'projects' / 'static')
STATICFILES_DIRS = [str(d) for d in _candidate_static_dirs if d.is_dir()]

# Cache configuration
# https://docs.djangoproject.com/en/5.2/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'academor-cache',
        'TIMEOUT': 7200,  # 2 hours default timeout
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Cache timeout settings (in seconds)
CACHE_TIMEOUT_SHORT = 1800  # 30 minutes for occasionally changing data
CACHE_TIMEOUT_MEDIUM = 7200  # 2 hours for normal pages (projects, vacancies lists)
CACHE_TIMEOUT_LONG = 86400  # 24 hours for stable data (about, contact, background images)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

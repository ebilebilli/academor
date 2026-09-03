from datetime import date
from pathlib import Path
import os
from academor.env_load import load_project_dotenv


load_project_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
#

##
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
if not (SECRET_KEY and str(SECRET_KEY).strip()):
    raise ValueError(
        'SECRET_KEY must be set to a non-empty value (e.g. in docker/.env for production).'
    )

# SECURITY WARNING: don't run with debug turned on in production!
def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ('true', '1', 'yes', 'on')


DEBUG = _env_bool('DEBUG', True)

# Cloudflare Turnstile (contact + review forms). Leave empty to disable widget/validation.
TURNSTILE_SITE_KEY = (os.getenv('TURNSTILE_SITE_KEY') or '').strip()
TURNSTILE_SECRET_KEY = (os.getenv('TURNSTILE_SECRET_KEY') or '').strip()

# Base hosts + optional extra from Docker / hosting (comma-separated). Empty env keeps defaults only.
_ALLOWED_BASE = ["academor.az", "www.academor.az"]
_extra_hosts = os.getenv("ALLOWED_HOSTS", "")
if _extra_hosts.strip():
    _from_env = [h.strip() for h in _extra_hosts.split(",") if h.strip()]
    ALLOWED_HOSTS = list(dict.fromkeys(_ALLOWED_BASE + _from_env))
else:
    ALLOWED_HOSTS = _ALLOWED_BASE

# Behind Nginx + Cloudflare: correct scheme for redirects, cookies, and security checks.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# YouTube embeds require a Referer header; same-origin blocks cross-origin Referer (Error 153).
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

CSRF_TRUSTED_ORIGINS = [
    "https://www.academor.az",
    'https://academor.az',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# CSRF Cookie Settings (allow env override for local Docker over plain HTTP)
CSRF_COOKIE_SECURE = _env_bool('CSRF_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

# Session Cookie Settings
SESSION_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', not DEBUG)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Portal Session (completely separate from Django admin session)
PORTAL_SESSION_COOKIE_NAME = 'portal_sessionid'
PORTAL_SESSION_COOKIE_PATH = '/portal/'  # Only sent on /portal/* URLs
PORTAL_SESSION_COOKIE_HTTPONLY = True
PORTAL_SESSION_COOKIE_SECURE = _env_bool('PORTAL_SESSION_COOKIE_SECURE', SESSION_COOKIE_SECURE)
PORTAL_SESSION_COOKIE_SAMESITE = 'Lax'

# Language cookie (synced with session on /i18n/setlang/)
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_SECURE = not DEBUG
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_SAMESITE = 'Lax'

# Absolute URLs in sitemap.xml (django.contrib.sites default is often example.com).
_ccd = (os.getenv('SITE_CANONICAL_DOMAIN') or 'academor.az').strip()
_ccd = _ccd.removeprefix('https://').removeprefix('http://').strip().rstrip('/')
SITE_CANONICAL_DOMAIN = _ccd or 'academor.az'

# Date-only lastmod for static URLs in sitemap (bump when static copy/nav changes meaningfully).
_slm = (os.getenv('SITEMAP_STATIC_LASTMOD') or '2026-04-14').strip()
try:
    SITEMAP_STATIC_LASTMOD = date.fromisoformat(_slm)
except ValueError:
    SITEMAP_STATIC_LASTMOD = date(2026, 4, 14)


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
    'imagekit',
    'ckeditor',
    'ckeditor_uploader',
    'compressor',

    # Apps
    'projects',
    'payments',
    'portals',
]

SITE_ID = 1

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        # Enables paste / drag-drop image upload (uploadimage plugin).
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': '/ckeditor/browse/',
        # Enhanced Image: Word-like drag handles to resize images in the editor.
        'extraPlugins': 'image2',
        'removePlugins': 'image',
        'image2_disableResizer': False,
        # Keep pasted math symbols, unicode, and Word formatting (do not auto-simplify).
        'allowedContent': True,
        'pasteFilter': None,
        'forcePasteAsPlainText': False,
        'pasteFromWordRemoveFontStyles': False,
        'pasteFromWordRemoveStyles': False,
        'pasteFromWordPromptCleanup': False,
        'entities': False,
        'basicEntities': True,
        'entities_latin': False,
        'entities_greek': False,
        'entities_processNumerical': False,
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'academor.middleware.CustomLocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Portal auth with completely separate cookie (portal_sessionid)
    'portals.middleware.PortalAuthenticationMiddleware',
    'portals.middleware.PortalSessionMiddleware',  # Sets/deletes portal_sessionid cookie
    'portals.middleware.PortalFragmentMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'academor.middleware.AdminAccessMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'academor.middleware.PublicHtmlCacheControlMiddleware',
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
                'projects.context_processors.turnstile_context',
                'projects.context_processors.page_banner_tagline_context',
                'portals.context_processors.portal_auth_context',
                'portals.context_processors.portal_notification_context',
                'portals.context_processors.portal_student_service_context',
                'portals.context_processors.portal_customer_service_context',
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
        'CONN_MAX_AGE': 60,
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'connect_timeout': 10,
        },
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

# SAT questions embed base64 images in HTML — allow larger admin POSTs.
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000


# Media / Static configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Static files directories (only paths that exist — avoids staticfiles.W004 in Docker)
_candidate_static_dirs = (BASE_DIR / 'static', BASE_DIR / 'projects' / 'static')
STATICFILES_DIRS = [str(d) for d in _candidate_static_dirs if d.is_dir()]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# Pre-built compressed bundles in production; DEBUG=True keeps separate script tags (easier debugging).
COMPRESS_OFFLINE = not DEBUG

# Production: hashed filenames so nginx can keep long Cache-Control + immutable safely.
# After deploy, HTML references new /static/.../file.<hash>.css; mobile won't reuse old URL.
if DEBUG:
    _STATICFILES_BACKEND = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    _STATICFILES_BACKEND = 'academor.storage.LenientManifestStaticFilesStorage'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': _STATICFILES_BACKEND,
    },
}

# Cache configuration
# https://docs.djangoproject.com/en/5.2/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'academor-cache',
        'TIMEOUT': 7200,  # 2 hours default timeout
        'OPTIONS': {
            'MAX_ENTRIES': 3000,
            'CULL_FREQUENCY': 4,
        }
    }
}

# DB only — cached_db + LocMemCache breaks language across gunicorn workers (each
# worker keeps its own stale session copy; F5 alternates az/en/ru randomly).
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Cache timeout settings (in seconds)
CACHE_TIMEOUT_SHORT = 1800  # 30 minutes for occasionally changing data
CACHE_TIMEOUT_MEDIUM = 7200  # 2 hours for normal pages (projects, vacancies lists)
CACHE_TIMEOUT_LONG = 86400  # 24 hours for stable data (about, contact, background images)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'portals.ielts_mock': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'portals.admin.quiz_options': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}


# United Payment Azerbaijan
UNITED_PAYMENT_AUTH_URL = os.getenv('UNITED_PAYMENT_AUTH_URL')
UNITED_PAYMENT_USERNAME = os.getenv('UNITED_PAYMENT_USERNAME')
UNITED_PAYMENT_PASSWORD = os.getenv('UNITED_PAYMENT_PASSWORD')
UNITED_PAYMENT_BASE_URL = os.getenv('UNITED_PAYMENT_BASE_URL')
UNITED_PAYMENT_SUCCESS_URL = os.getenv('UNITED_PAYMENT_SUCCESS_URL')
UNITED_PAYMENT_CANCEL_URL = os.getenv('UNITED_PAYMENT_CANCEL_URL')
UNITED_PAYMENT_DECLINE_URL = os.getenv('UNITED_PAYMENT_DECLINE_URL')

# Optional: where to redirect user after bank callback.
# If empty, backend will render payment/success.html or payment/failed.html.
# Example: https://academor.az/payment-result
PAYMENT_FRONTEND_RETURN_URL = (os.getenv('PAYMENT_FRONTEND_RETURN_URL') or '').strip()
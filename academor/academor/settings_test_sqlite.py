"""
Test-only settings: run the test suite against local SQLite when the
Dockerized Postgres is unavailable. Never used in production.

Usage: python manage.py test --settings=academor.settings_test_sqlite
"""
from academor.settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# LocMemCache survives across test cases while the DB rolls back, which makes
# @cached_query results stale and tests order-dependent.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
COMPRESS_OFFLINE = False
COMPRESS_ENABLED = False
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

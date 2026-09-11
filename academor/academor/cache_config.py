"""Shared CACHES construction for settings.py and settings_local.py.

Runtime uses Redis only (REDIS_HOST required). LocMem is gone from the app
path — it was per-worker and defeated @cached_query sharing. Tests use
DummyCache so cases stay independent of each other and of gunicorn's Redis.
"""
from __future__ import annotations

import os
import sys
from urllib.parse import quote


def running_django_tests() -> bool:
    return len(sys.argv) >= 2 and sys.argv[1] == 'test'


def _test_caches() -> dict:
    return {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }


def redis_location(
    *,
    host: str | None = None,
    port: str | None = None,
    password: str | None = None,
    db: str | None = None,
) -> str:
    host = (host if host is not None else os.getenv('REDIS_HOST', '')).strip()
    port = (port if port is not None else os.getenv('REDIS_PORT', '6379')).strip() or '6379'
    password = (
        password if password is not None else os.getenv('REDIS_PASSWORD', '')
    ).strip()
    db = (db if db is not None else os.getenv('REDIS_CACHE_DB', '1')).strip() or '1'
    if password:
        return f'redis://:{quote(password, safe="")}@{host}:{port}/{db}'
    return f'redis://{host}:{port}/{db}'


def build_caches(*, force_tests: bool | None = None) -> dict:
    """Redis for the app; DummyCache only while ``manage.py test`` runs."""
    if force_tests is None:
        force_tests = running_django_tests()
    if force_tests:
        return _test_caches()

    host = (os.getenv('REDIS_HOST') or '').strip()
    if not host:
        raise ValueError(
            'REDIS_HOST must be set for Django CACHES. Compose injects '
            'REDIS_HOST=redis; add REDIS_PASSWORD to docker/.env if needed. '
            'LocMem is no longer used at runtime.'
        )
    return {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': redis_location(host=host),
            'TIMEOUT': 7200,
            'KEY_PREFIX': 'academor',
            'OPTIONS': {
                'socket_connect_timeout': 2,
                'socket_timeout': 2,
            },
        }
    }

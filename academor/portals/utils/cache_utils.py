"""
Portal cache utilities — separate version key from the public site (projects).

@cached_query / invalidate_model_cache here use ``portals_cache_version`` so portal
admin changes do not flush the marketing site cache (and vice versa).
"""
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language

import hashlib

_CACHE_MISS = object()
_PORTALS_VERSION_KEY = 'portals_cache_version'


def _resolve_cache_timeout(timeout, timeout_settings_key=None):
    try:
        if timeout_settings_key:
            return getattr(
                settings,
                timeout_settings_key,
                getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300),
            )
        if callable(timeout):
            return timeout()
        if timeout is None:
            return getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)
        return int(timeout)
    except Exception:
        return getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)


def _get_cache_version():
    try:
        return cache.get(_PORTALS_VERSION_KEY, 0)
    except Exception:
        return 0


def generate_cache_key(prefix, *args, **kwargs):
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
    filtered_kwargs.setdefault('lang', get_language())
    sorted_kwargs = sorted(filtered_kwargs.items())

    def safe_str(val):
        if val is None:
            return 'None'
        if isinstance(val, (list, tuple)):
            return ','.join(str(item) for item in val)
        if isinstance(val, dict):
            return ','.join(f'{k}:{v}' for k, v in sorted(val.items()))
        return str(val)

    key_parts = (
        [prefix]
        + [safe_str(arg) for arg in args]
        + [f'{k}={safe_str(v)}' for k, v in sorted_kwargs]
    )
    key_string = '|'.join(key_parts)
    if len(key_string) > 200:
        key_string = hashlib.md5(key_string.encode()).hexdigest()
        return f'portals:{prefix}:{key_string}'
    return f'portals:{key_string}'


def get_query_cache_key(query_name, *args, **kwargs):
    return generate_cache_key(f'query_{query_name}', *args, **kwargs)


def get_page_cache_key(view_name, user_id, **query_params):
    sorted_params = sorted(query_params.items())
    return generate_cache_key(f'page_{view_name}', user_id, **dict(sorted_params))


def cached_query(timeout=None):
    timeout_settings_key = None
    if isinstance(timeout, str):
        timeout_settings_key = timeout
        timeout = None

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_timeout = _resolve_cache_timeout(timeout, timeout_settings_key)
            cache_version = _get_cache_version()
            try:
                cache_key = get_query_cache_key(
                    func.__name__,
                    *args,
                    cache_version=cache_version,
                    **kwargs,
                )
            except Exception:
                return func(*args, **kwargs)

            try:
                result = cache.get(cache_key, _CACHE_MISS)
                if result is not _CACHE_MISS:
                    return result
            except Exception:
                pass

            result = func(*args, **kwargs)
            try:
                ttl = min(cache_timeout, 60) if result is None else cache_timeout
                cache.set(cache_key, result, ttl)
            except Exception:
                pass
            return result

        return wrapper

    return decorator


def cached_page_data(timeout=None):
    timeout_settings_key = None
    if isinstance(timeout, str):
        timeout_settings_key = timeout
        timeout = None

    def decorator(func):
        @wraps(func)
        def wrapper(request, profile_id, *args, **kwargs):
            cache_timeout = _resolve_cache_timeout(timeout, timeout_settings_key)
            cache_version = _get_cache_version()
            try:
                query_params = dict(request.GET.items())
                view_name = func.__name__.replace('get_', '').replace('_data', '')
                cache_key = get_page_cache_key(
                    view_name,
                    profile_id,
                    cache_version=cache_version,
                    **query_params,
                )
            except Exception:
                return func(request, profile_id, *args, **kwargs)

            try:
                result = cache.get(cache_key, _CACHE_MISS)
                if result is not _CACHE_MISS:
                    return result
            except Exception:
                pass

            result = func(request, profile_id, *args, **kwargs)
            try:
                ttl = min(cache_timeout, 60) if result is None else cache_timeout
                cache.set(cache_key, result, ttl)
            except Exception:
                pass
            return result

        return wrapper

    return decorator


def _bump_cache_version():
    try:
        current_version = cache.get(_PORTALS_VERSION_KEY, 0)
        cache.set(_PORTALS_VERSION_KEY, current_version + 1, None)
    except Exception:
        pass


def invalidate_page_cache(view_names=None):
    _bump_cache_version()


def invalidate_query_cache(query_names=None):
    _bump_cache_version()


def invalidate_model_cache(model_name):
    """Bump portals cache version when portal ORM data changes."""
    _bump_cache_version()

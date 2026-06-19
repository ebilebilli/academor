"""
Cache utilities for page-level caching and cache invalidation.

Versioned keys: @cached_query and @cached_page_data embed cache.get('cache_version').
invalidate_model_cache (and invalidate_*_cache) bumps that integer so all such entries miss.

When adding a new cached function that reads the DB, register post_save/post_delete in
projects.signals so content changes are visible (see module docstring there).

Note: QuerySet.update() / bulk_create(..., ignore_conflicts) bypass model signals;
prefer Model.save() in admin or call invalidate_page_cache manually after bulk ops.
LocMemCache is per-process; use a shared backend if you run multiple workers.
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
# from django.utils.cache import get_cache_key
import hashlib
_CACHE_MISS = object()


def _resolve_cache_timeout(timeout, timeout_settings_key=None):
    """Resolve cache timeout from literal/callable/settings key with safe fallback."""
    try:
        if timeout_settings_key:
            return getattr(settings, timeout_settings_key, getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300))
        if callable(timeout):
            return timeout()
        if timeout is None:
            return getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)
        return int(timeout)
    except Exception:
        return getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)


def _get_cache_version():
    try:
        return cache.get('cache_version', 0)
    except Exception:
        return 0

# import json


def generate_cache_key(prefix, *args, **kwargs):
    """
    Generate a cache key from prefix and arguments.
    
    Args:
        prefix: Cache key prefix (e.g., 'page_home', 'query_projects')
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key (None values are skipped)
    
    Returns:
        str: Generated cache key
    """
    # Filter out None values from kwargs for consistent key generation
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
    
    # Sort kwargs for consistent key generation
    sorted_kwargs = sorted(filtered_kwargs.items())
    
    # Create a string representation of all arguments
    # Handle different types properly
    def safe_str(val):
        if val is None:
            return 'None'
        elif isinstance(val, (list, tuple)):
            return ','.join(str(item) for item in val)
        elif isinstance(val, dict):
            return ','.join(f"{k}:{v}" for k, v in sorted(val.items()))
        else:
            return str(val)
    
    key_parts = [prefix] + [safe_str(arg) for arg in args] + [f"{k}={safe_str(v)}" for k, v in sorted_kwargs]
    key_string = "|".join(key_parts)
    
    # Hash the key if it's too long (Django cache keys have length limits)
    if len(key_string) > 200:
        key_string = hashlib.md5(key_string.encode()).hexdigest()
        return f"academor:{prefix}:{key_string}"
    
    return f"academor:{key_string}"


def get_page_cache_key(view_name, lang, **query_params):
    """
    Generate cache key for a page view.
    
    Args:
        view_name: Name of the view (e.g., 'home', 'project-list')
        lang: Language code
        **query_params: Query parameters from request.GET
    
    Returns:
        str: Cache key for the page
    """
    # Sort query params for consistent keys
    sorted_params = sorted(query_params.items())
    return generate_cache_key(f"page_{view_name}", lang, **dict(sorted_params))


def get_query_cache_key(query_name, *args, **kwargs):
    """
    Generate cache key for a database query.
    
    Args:
        query_name: Name of the query function (e.g., 'projects', 'about')
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        str: Cache key for the query
    """
    return generate_cache_key(f"query_{query_name}", *args, **kwargs)


def cached_query(timeout=None):
    """
    Decorator to cache the result of a query function.
    
    Args:
        timeout: Cache timeout in seconds, callable function, or None (uses CACHE_TIMEOUT_MEDIUM).
                 Can also be string like 'CACHE_TIMEOUT_LONG' to read from settings.
    
    Usage:
        @cached_query(timeout=300)
        @cached_query(timeout=getattr(settings, 'CACHE_TIMEOUT_LONG', 3600))
        def get_projects(lang='az', category_slug=None):
            ...
    """
    # If timeout is a string, it's a settings attribute name
    timeout_settings_key = None
    if isinstance(timeout, str):
        timeout_settings_key = timeout
        timeout = None
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_timeout = _resolve_cache_timeout(timeout, timeout_settings_key)
            
            # Generate cache key from function name and arguments
            # Include cache version for invalidation support
            cache_version = _get_cache_version()
            
            # Generate cache key with all parameters
            try:
                cache_key = get_query_cache_key(
                    func.__name__, 
                    *args, 
                    cache_version=cache_version,
                    **kwargs
                )
            except Exception as e:
                # If key generation fails, skip caching
                return func(*args, **kwargs)
            
            # Try to get from cache
            try:
                result = cache.get(cache_key, _CACHE_MISS)
                if result is not _CACHE_MISS:
                    return result
            except Exception:
                # If cache read fails, continue without cache
                pass
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                # Cache result (including None values, but with shorter timeout)
                try:
                    if result is None:
                        # Cache None values with shorter timeout
                        cache.set(cache_key, result, min(cache_timeout, 60))
                    else:
                        # Cache actual values with full timeout
                        cache.set(cache_key, result, cache_timeout)
                except Exception:
                    # If cache write fails, just return result without caching
                    pass
                return result
            except Exception:
                # If function fails, don't cache the error, just raise it
                raise
        return wrapper
    return decorator


def _bump_cache_version():
    """Increment global cache version to invalidate all versioned cache entries."""
    try:
        current_version = cache.get('cache_version', 0)
        cache.set('cache_version', current_version + 1, None)
    except Exception:
        pass


def invalidate_page_cache(view_names=None):
    """
    Invalidate all page caches via version bump.
    
    Note: locmem/Redis backends don't support key-pattern deletion, so this
    always does a full version-based invalidation regardless of view_names.
    Sessions and other non-versioned keys are NOT affected.
    """
    _bump_cache_version()


def invalidate_query_cache(query_names=None):
    """
    Invalidate all query caches via version bump.
    
    Note: locmem/Redis backends don't support key-pattern deletion, so this
    always does a full version-based invalidation regardless of query_names.
    """
    _bump_cache_version()


def cached_page_data(timeout=None):
    """
    Decorator to cache page data functions (like get_home_page_data, get_project_list_data).
    
    Args:
        timeout: Cache timeout in seconds, callable function, or None (uses CACHE_TIMEOUT_MEDIUM).
                 Can also be string like 'CACHE_TIMEOUT_MEDIUM' to read from settings.
    
    Usage:
        @cached_page_data(timeout=300)
        @cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
        def get_home_page_data(request, lang):
            ...
    """
    # If timeout is a string, it's a settings attribute name
    timeout_settings_key = None
    if isinstance(timeout, str):
        timeout_settings_key = timeout
        timeout = None
    
    def decorator(func):
        @wraps(func)
        def wrapper(request, lang, *args, **kwargs):
            cache_timeout = _resolve_cache_timeout(timeout, timeout_settings_key)
            
            # Generate cache key from function name, language, and query parameters
            # Include cache version for invalidation support
            cache_version = _get_cache_version()
            
            try:
                query_params = dict(request.GET.items())
                view_name = func.__name__.replace('get_', '').replace('_data', '')
                cache_key = get_page_cache_key(view_name, lang, cache_version=cache_version, **query_params)
            except Exception:
                # If key generation fails, skip caching
                return func(request, lang, *args, **kwargs)
            
            # Try to get from cache
            try:
                result = cache.get(cache_key, _CACHE_MISS)
                if result is not _CACHE_MISS:
                    return result
            except Exception:
                # If cache read fails, continue without cache
                pass
            
            # Execute function and cache result
            try:
                result = func(request, lang, *args, **kwargs)
                # Always cache result (including None, but with shorter timeout)
                try:
                    if result is None:
                        cache.set(cache_key, result, min(cache_timeout, 60))
                    else:
                        cache.set(cache_key, result, cache_timeout)
                except Exception:
                    # If cache write fails, just return result without caching
                    pass
                return result
            except Exception:
                # If function fails, don't cache the error, just raise it
                raise
        return wrapper
    return decorator


def invalidate_model_cache(model_name):
    """
    Bump global cache_version so all @cached_query / @cached_page_data keys miss.

    Args:
        model_name: Which model changed (documentation / future metrics only; not used for keying).

    Service (e.g. admin ``card_icon`` dropdown) uses the same bump — see
    ``projects.signals.invalidate_service_cache``.

    Tagline changes bump all versioned keys (inner-page banner taglines).
    CoursePricePackage changes bump via ``invalidate_course_price_package_cache`` (Service).
    """
    _bump_cache_version()


def invalidate_sale_cache():
    """
    Bump cache version for all homepage promotion + course discount data.

    Invalidates:
    - ``get_serialized_active_sales`` / ``get_home_sales_context`` (homepage banner)
    - ``get_active_sale_discounts_by_service_id`` (service-card ``on_sale`` labels, checkout)
    - Cached page blobs that embed ``serialize_project_category`` / ``serialize_price_package``

    Called from Sale signals, Media linked to a Sale, and SaleAdmin list_editable saves
    (QuerySet.update bypasses post_save).
    """
    _bump_cache_version()


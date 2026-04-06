"""
Cache utilities for page-level caching and cache invalidation.
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


def invalidate_page_cache(view_names=None):
    """
    Invalidate cache for specific pages or all pages.
    
    Args:
        view_names: List of view names to invalidate. If None, invalidates all pages.
    """
    if view_names is None:
        # Invalidate all page caches (using a pattern - simple but works with locmem)
        # For production with Redis, you could use pattern matching
        cache.clear()
    else:
        # For specific views, we'd need to track keys or use version-based invalidation
        # For now, we'll use a version-based approach
        cache.set('cache_version', cache.get('cache_version', 0) + 1, None)


def invalidate_query_cache(query_names=None):
    """
    Invalidate cache for specific queries or all queries.
    
    Args:
        query_names: List of query names to invalidate. If None, invalidates all queries.
    """
    if query_names is None:
        # Increment cache version to invalidate all queries
        current_version = cache.get('cache_version', 0)
        cache.set('cache_version', current_version + 1, None)
    else:
        # Increment cache version to invalidate specific queries
        # Since we can't pattern match with locmem cache, we invalidate all
        current_version = cache.get('cache_version', 0)
        cache.set('cache_version', current_version + 1, None)


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
    Invalidate all cache entries related to a specific model.
    
    Args:
        model_name: Name of the model (e.g., 'Project', 'Vacancy', 'About', 'Media', 'Motto')
    """
    # Increment cache version to invalidate all related caches
    # This ensures all cache keys with cache_version parameter are invalidated
    try:
        current_version = cache.get('cache_version', 0)
        cache.set('cache_version', current_version + 1, None)
    except Exception:
        # If cache version update fails, clear all cache as fallback
        try:
            cache.clear()
        except Exception:
            pass


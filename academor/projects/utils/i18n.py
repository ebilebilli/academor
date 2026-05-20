"""Public site language resolution (shared by middleware and views)."""
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.conf import settings

PUBLIC_LANGUAGE_CODES = frozenset({'az', 'en', 'ru'})


def normalize_lang(code):
    lang = (code or '').lower().split('-')[0]
    return lang if lang in PUBLIC_LANGUAGE_CODES else None


def resolve_public_language(request):
    """
    Single source of truth for UI language on public pages.

    Priority matches CustomLocaleMiddleware:
    1. Session (when user explicitly chose a language)
    2. Language cookie
    3. Session fallback (e.g. ?lang= without language_user_chosen yet)
    4. Site default (LANGUAGE_CODE)
    """
    if request.session.get('language_user_chosen'):
        lang = normalize_lang(
            request.session.get('django_language') or request.session.get('language')
        )
        if lang:
            return lang

    cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
    lang = normalize_lang(request.COOKIES.get(cookie_name, ''))
    if lang:
        return lang

    lang = normalize_lang(
        request.session.get('django_language') or request.session.get('language')
    )
    if lang:
        return lang

    default = normalize_lang(getattr(settings, 'LANGUAGE_CODE', 'az'))
    return default or 'az'


def strip_lang_query_params(url):
    """Remove ?lang= / ?language= so redirect after switch cannot reset the session."""
    parsed = urlparse(url)
    if not parsed.query:
        return url
    params = parse_qs(parsed.query, keep_blank_values=True)
    changed = False
    for key in ('lang', 'language'):
        if key in params:
            del params[key]
            changed = True
    if not changed:
        return url
    return urlunparse(parsed._replace(query=urlencode(params, doseq=True)))


def apply_language_cookie(response, language):
    """Write django_language cookie on a response (redirect or HTML)."""
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=getattr(settings, 'LANGUAGE_COOKIE_AGE', None),
        path=getattr(settings, 'LANGUAGE_COOKIE_PATH', '/'),
        domain=getattr(settings, 'LANGUAGE_COOKIE_DOMAIN', None),
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    return response


def sync_language_cookie_on_response(request, response):
    """
    Keep cookie aligned with session after user chose a language.

    If set_language set session but the cookie was dropped (proxy, old tab),
    later requests would still render correctly from session, but some clients
    only send cookie — sync on every HTML response avoids drift.
    """
    if not request.session.get('language_user_chosen'):
        return response
    lang = normalize_lang(
        request.session.get('django_language') or request.session.get('language')
    )
    if not lang:
        return response
    cookie_name = settings.LANGUAGE_COOKIE_NAME
    if request.COOKIES.get(cookie_name) == lang:
        return response
    return apply_language_cookie(response, lang)

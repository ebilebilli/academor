"""Public site language resolution (shared by middleware and views)."""
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

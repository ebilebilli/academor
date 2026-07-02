from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import translation
from django.conf import settings

from projects.utils.i18n import normalize_lang, resolve_public_language, sync_language_cookie_on_response
from portals.utils.admin_access import can_access_django_admin


class PublicHtmlCacheControlMiddleware:
    """
    HTML səhifələri üçün brauzer/CDN-də köhnə versiyanın yapışmaması.
    Statik fayllar nginx-də uzun müddət keşlənir + immutable; onların URL-ləri
    ManifestStaticFilesStorage ilə hər deploy-da dəyişir — yeni HTML həmişə
    yeni hash-lı statikə işarə etməlidir (xüsusən mobil Safari/Chrome).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.DEBUG:
            return response
        content_type = (response.get('Content-Type') or '').split(';')[0].strip().lower()
        if content_type == 'text/html' and response.status_code == 200:
            if 'Cache-Control' not in response:
                response['Cache-Control'] = 'private, no-cache, must-revalidate'
            if 'Vary' not in response:
                response['Vary'] = 'Cookie, Accept-Language'
        return response


class AdminAccessMiddleware:
    """
    Block portal-only accounts from Django admin.
    Portal session (portal_sessionid cookie) is completely separate from
    Django admin session (sessionid cookie), so logout here doesn't affect portal.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_prefix = f'/{settings.ADMIN_URL.strip("/")}'

    def __call__(self, request):
        if (
            request.path.startswith(self.admin_prefix)
            and request.user.is_authenticated
            and not can_access_django_admin(request.user)
        ):
            # Logout from Django admin session only (sessionid cookie).
            # Portal session (portal_sessionid) is completely separate and untouched.
            logout(request)
            messages.error(
                request,
                'This account uses the student portal only. Log in from the main website.',
            )
            return redirect(f'{self.admin_prefix}/login/')
        return self.get_response(request)


class CustomLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_prefix = f'/{settings.ADMIN_URL.strip("/")}'
        if request.path.startswith(admin_prefix):
            admin_lang = normalize_lang(getattr(settings, 'ADMIN_LANGUAGE_CODE', 'en')) or 'en'
            translation.activate(admin_lang)
            request.LANGUAGE_CODE = admin_lang
            return self.get_response(request)

        language = resolve_public_language(request)
        translation.activate(language)
        request.LANGUAGE_CODE = language

        response = self.get_response(request)
        return sync_language_cookie_on_response(request, response)

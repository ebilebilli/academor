from django.utils import translation
from django.conf import settings

from projects.utils.i18n import normalize_lang, resolve_public_language


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
        return self.get_response(request)

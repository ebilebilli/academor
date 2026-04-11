from django.utils import translation
from django.conf import settings


class CustomLocaleMiddleware:
    LANGUAGES = {
        'az': 'Azərbaycan',
        'en': 'English',
        'ru': 'Русский',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_prefix = f'/{settings.ADMIN_URL.strip("/")}'
        if request.path.startswith(admin_prefix):
            admin_lang = getattr(settings, 'ADMIN_LANGUAGE_CODE', 'en')
            translation.activate(admin_lang)
            request.LANGUAGE_CODE = admin_lang
            return self.get_response(request)

        language = request.session.get('django_language') or request.session.get('language')
        if language and language in self.LANGUAGES:
            translation.activate(language)
            request.LANGUAGE_CODE = language
        else:
            site_default = getattr(settings, 'LANGUAGE_CODE', 'az')
            if site_default not in self.LANGUAGES:
                site_default = 'az'
            translation.activate(site_default)
            request.LANGUAGE_CODE = site_default

        return self.get_response(request)

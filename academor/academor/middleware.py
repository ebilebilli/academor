from django.utils import translation
from django.conf import settings


class CustomLocaleMiddleware:
    DEFAULT_LANGUAGE = 'az'
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
            translation.activate(self.DEFAULT_LANGUAGE)
            request.LANGUAGE_CODE = self.DEFAULT_LANGUAGE
            return self.get_response(request)

        language = request.session.get('django_language') or request.session.get('language')
        if language and language in self.LANGUAGES:
            translation.activate(language)
            request.LANGUAGE_CODE = language
        else:
            translation.activate(self.DEFAULT_LANGUAGE)
            request.LANGUAGE_CODE = self.DEFAULT_LANGUAGE

        return self.get_response(request)

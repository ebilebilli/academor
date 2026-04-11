from django.http import HttpResponseRedirect
from django.utils import translation
from django.conf import settings

def set_language(request):
    next_url = request.POST.get('next') or request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    admin_path = f'/{settings.ADMIN_URL.strip("/")}/'
    is_admin = next_url.startswith(admin_path)

    language = request.POST.get('language') or request.GET.get('language')

    if language and language in dict(settings.LANGUAGES):
        if is_admin:
            admin_lang = getattr(settings, 'ADMIN_LANGUAGE_CODE', 'en')
            request.session['admin_language'] = admin_lang
            translation.activate(admin_lang)
        else:
            request.session['django_language'] = language
            request.session['language'] = language  
            request.session.modified = True
            request.session.save()

            translation.activate(language)

    return HttpResponseRedirect(next_url)

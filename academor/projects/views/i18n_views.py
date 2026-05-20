from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import check_for_language


def _safe_next_url(request, raw_next):
    next_url = (raw_next or '').strip() or '/'
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return '/'
    return next_url


def set_language(request):
    next_url = _safe_next_url(
        request,
        request.POST.get('next') or request.GET.get('next') or request.META.get('HTTP_REFERER'),
    )
    admin_path = f'/{settings.ADMIN_URL.strip("/")}/'
    is_admin = next_url.startswith(admin_path)

    language = request.POST.get('language') or request.GET.get('language')

    response = HttpResponseRedirect(next_url)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'

    if not (language and check_for_language(language)):
        return response

    if is_admin:
        admin_lang = getattr(settings, 'ADMIN_LANGUAGE_CODE', 'en')
        request.session['admin_language'] = admin_lang
        translation.activate(admin_lang)
        return response

    if not request.session.session_key:
        request.session.create()

    request.session['django_language'] = language
    request.session['language'] = language
    request.session['language_user_chosen'] = True
    request.session.modified = True
    request.session.save()

    translation.activate(language)
    request.LANGUAGE_CODE = language

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

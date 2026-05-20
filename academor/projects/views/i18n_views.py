from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import check_for_language
from django.views.decorators.http import require_POST

from projects.utils.i18n import apply_language_cookie, normalize_lang, strip_lang_query_params


def _safe_next_url(request, raw_next):
    next_url = (raw_next or '').strip() or '/'
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return '/'
    return strip_lang_query_params(next_url)


@require_POST
def set_language(request):
    next_url = _safe_next_url(
        request,
        request.POST.get('next') or request.META.get('HTTP_REFERER'),
    )
    admin_path = f'/{settings.ADMIN_URL.strip("/")}/'
    is_admin = next_url.startswith(admin_path)

    language = normalize_lang(request.POST.get('language', ''))

    response = HttpResponseRedirect(next_url)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Vary'] = 'Cookie'

    if not (language and check_for_language(language)):
        return response

    if is_admin:
        admin_lang = normalize_lang(getattr(settings, 'ADMIN_LANGUAGE_CODE', 'en')) or 'en'
        request.session['admin_language'] = admin_lang
        translation.activate(admin_lang)
        return response

    if not request.session.session_key:
        request.session.create()

    request.session['django_language'] = language
    request.session['language'] = language
    request.session['language_user_chosen'] = True
    request.session.modified = True

    translation.activate(language)
    request.LANGUAGE_CODE = language

    apply_language_cookie(response, language)
    return response

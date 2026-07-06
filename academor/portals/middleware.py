from django.conf import settings
from django.utils.functional import SimpleLazyObject

from portals.utils.portal_fragment import (
    build_fragment_document,
    is_portal_fragment_request,
)
from portals.utils.portal_session import (
    PORTAL_COOKIE_NAME,
    PORTAL_COOKIE_PATH,
    PORTAL_COOKIE_HTTPONLY,
    PORTAL_COOKIE_SECURE,
    PORTAL_COOKIE_SAMESITE,
    get_portal_user,
)


class PortalAuthenticationMiddleware:
    """
    Attach portal session user separately from Django admin auth.
    Uses completely separate 'portal_sessionid' cookie.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.portal_user = SimpleLazyObject(lambda: get_portal_user(request))
        return self.get_response(request)


class PortalSessionMiddleware:
    """
    Manage portal session cookie separately from Django's sessionid.
    - Sets portal_sessionid cookie on login
    - Deletes cookie on logout
    - Cookie only sent on /portal/* paths
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Login: save session and set cookie
        if hasattr(request, '_portal_session'):
            session = request._portal_session
            response.set_cookie(
                PORTAL_COOKIE_NAME,
                session.session_key,
                max_age=settings.SESSION_COOKIE_AGE,
                httponly=PORTAL_COOKIE_HTTPONLY,
                secure=PORTAL_COOKIE_SECURE,
                samesite=PORTAL_COOKIE_SAMESITE,
                path=PORTAL_COOKIE_PATH,
            )

        # Logout: delete cookie
        if getattr(request, '_portal_session_cleared', False):
            response.delete_cookie(
                PORTAL_COOKIE_NAME,
                path=PORTAL_COOKIE_PATH,
            )

        return response


class PortalFragmentMiddleware:
    """Return lightweight HTML for portal AJAX navigation (no sidebar/topbar)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not is_portal_fragment_request(request):
            return response
        if response.status_code != 200:
            return response
        content_type = response.get('Content-Type', '')
        if 'text/html' not in content_type:
            return response

        charset = getattr(response, 'charset', None) or 'utf-8'
        try:
            html = response.content.decode(charset)
            fragment = build_fragment_document(html)
            if fragment and fragment != html:
                response.content = fragment.encode(charset)
                if 'Content-Length' in response:
                    response['Content-Length'] = str(len(response.content))
        except Exception as exc:
            import logging

            logging.getLogger('portals.fragment').warning(
                'Portal fragment extraction failed: %s',
                exc,
                exc_info=True,
            )
        return response


# DEPRECATED: No longer needed with separate cookies — kept only so old
# settings imports do not break; remove once confirmed unused in all envs.
class AuthRealmIsolationMiddleware:
    """
    DEPRECATED: Separate cookies make this unnecessary.
    Kept for backward compatibility - does nothing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

"""
Portal Session - Completely separate session from Django admin auth.

Uses a separate cookie 'portal_sessionid' that only sends on /portal/* paths.
No interference with Django's default 'sessionid' cookie used by admin.
"""
from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

PORTAL_SESSION_USER_KEY = '_portal_auth_user_id'
QUIZ_START_KEY_PREFIX = '_quiz_start_'
QUIZ_QUESTIONS_KEY_PREFIX = '_quiz_questions_'
PORTAL_COOKIE_NAME = getattr(settings, 'PORTAL_SESSION_COOKIE_NAME', 'portal_sessionid')
PORTAL_COOKIE_PATH = getattr(settings, 'PORTAL_SESSION_COOKIE_PATH', '/portal/')
PORTAL_COOKIE_HTTPONLY = getattr(settings, 'PORTAL_SESSION_COOKIE_HTTPONLY', True)
PORTAL_COOKIE_SECURE = getattr(settings, 'PORTAL_SESSION_COOKIE_SECURE', False)
PORTAL_COOKIE_SAMESITE = getattr(settings, 'PORTAL_SESSION_COOKIE_SAMESITE', 'Lax')

User = get_user_model()


class PortalSessionStore(DBStore):
    """Custom session store for portal - completely separate from admin session."""
    pass


_SESSION_CACHE_ATTR = '_portal_session_store'


def _get_portal_session(request):
    """Get or create portal session from separate cookie.

    Cached on the request: the session helpers are called several times per
    request (middleware, mixins, context processors) and each fresh store
    re-reads the session row from the DB.
    """
    store = getattr(request, _SESSION_CACHE_ATTR, None)
    if store is None:
        cookie_val = request.COOKIES.get(PORTAL_COOKIE_NAME)
        store = PortalSessionStore(cookie_val)
        setattr(request, _SESSION_CACHE_ATTR, store)
    return store


def _save_portal_session(request, session):
    """Mark session to be saved and attach to request for middleware."""
    session.save()
    request._portal_session = session


def _clear_portal_session_flag(request):
    """Mark session for deletion."""
    request._portal_session_cleared = True


def portal_login(request, user) -> None:
    """
    Login user to portal session only.
    Does NOT touch Django's session or request.user.
    """
    session = _get_portal_session(request)
    session[PORTAL_SESSION_USER_KEY] = user.pk
    _save_portal_session(request, session)


def portal_logout(request) -> None:
    """Logout from portal only - admin session untouched."""
    session = _get_portal_session(request)
    session.flush()
    _clear_portal_session_flag(request)


def get_portal_user_id(request) -> int | None:
    """Get portal user ID from separate session cookie."""
    if not request.COOKIES.get(PORTAL_COOKIE_NAME) and getattr(request, _SESSION_CACHE_ATTR, None) is None:
        return None
    try:
        store = _get_portal_session(request)
        value = store.get(PORTAL_SESSION_USER_KEY)
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def get_portal_user(request):
    """Get user from portal session - completely separate from request.user."""
    user_id = get_portal_user_id(request)
    if not user_id:
        return AnonymousUser()
    try:
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        # Clean up invalid session
        session = _get_portal_session(request)
        session.pop(PORTAL_SESSION_USER_KEY, None)
        session.save()
        return AnonymousUser()


def is_portal_authenticated(request) -> bool:
    """Check if user is authenticated via portal session only."""
    return get_portal_user_id(request) is not None


def clear_portal_session(request) -> None:
    """Clear portal session - for signal use."""
    session = _get_portal_session(request)
    session.pop(PORTAL_SESSION_USER_KEY, None)
    session.save()
    _clear_portal_session_flag(request)


def clear_portal_session_on_admin_login(request) -> None:
    """Admin login - portal stays logged in (separate cookies)."""
    # No-op: separate cookies means no conflict
    pass


def get_portal_session_store(request) -> PortalSessionStore:
    pending = getattr(request, '_portal_session', None)
    if pending is not None:
        return pending
    return _get_portal_session(request)


def ensure_portal_session(request) -> PortalSessionStore:
    session = get_portal_session_store(request)
    if not session.session_key:
        session.create()
    return session


def set_portal_session_value(request, key, value) -> None:
    session = ensure_portal_session(request)
    session[key] = value
    _save_portal_session(request, session)


def get_portal_session_value(request, key, default=None):
    session = get_portal_session_store(request)
    if not session.session_key:
        return default
    return session.get(key, default)


def pop_portal_session_value(request, key, default=None):
    session = ensure_portal_session(request)
    value = session.pop(key, default)
    _save_portal_session(request, session)
    return value


def quiz_start_session_key(quiz_id: int) -> str:
    return f'{QUIZ_START_KEY_PREFIX}{quiz_id}'


def set_quiz_attempt_start(request, quiz_id: int) -> None:
    from django.utils import timezone

    set_portal_session_value(
        request,
        quiz_start_session_key(quiz_id),
        timezone.now().isoformat(),
    )


def get_quiz_attempt_start(request, quiz_id: int):
    return get_portal_session_value(request, quiz_start_session_key(quiz_id))


def clear_quiz_attempt_start(request, quiz_id: int) -> None:
    pop_portal_session_value(request, quiz_start_session_key(quiz_id))


def quiz_questions_session_key(quiz_id: int) -> str:
    return f'{QUIZ_QUESTIONS_KEY_PREFIX}{quiz_id}'


def get_quiz_attempt_question_ids(request, quiz_id: int) -> list[int] | None:
    raw = get_portal_session_value(request, quiz_questions_session_key(quiz_id))
    if not isinstance(raw, list) or not raw:
        return None
    ids = []
    for item in raw:
        try:
            ids.append(int(item))
        except (TypeError, ValueError):
            continue
    return ids or None


def set_quiz_attempt_question_ids(request, quiz_id: int, question_ids: list[int]) -> None:
    set_portal_session_value(request, quiz_questions_session_key(quiz_id), question_ids)


def clear_quiz_attempt_question_ids(request, quiz_id: int) -> None:
    pop_portal_session_value(request, quiz_questions_session_key(quiz_id))

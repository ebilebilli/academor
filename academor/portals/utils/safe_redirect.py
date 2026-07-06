"""Validation for client-supplied redirect targets ("next" parameters)."""
from django.utils.http import url_has_allowed_host_and_scheme

PORTAL_PATH_PREFIX = '/portal'


def safe_portal_next_url(request, candidate: str | None) -> str:
    """
    Return the candidate redirect path only if it is a safe, same-origin
    portal path. Rejects protocol-relative URLs like ``/portal//evil.com``
    and anything outside the portal prefix. Returns '' when unsafe.
    """
    candidate = (candidate or '').strip()
    if not candidate.startswith(PORTAL_PATH_PREFIX):
        return ''
    if not url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return ''
    return candidate

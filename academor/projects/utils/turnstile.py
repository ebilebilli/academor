import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'


def is_turnstile_configured():
    return bool(
        (getattr(settings, 'TURNSTILE_SITE_KEY', '') or '').strip()
        and (getattr(settings, 'TURNSTILE_SECRET_KEY', '') or '').strip()
    )


def verify_turnstile_response(token, remote_ip=None):
    if not is_turnstile_configured():
        return True

    secret = settings.TURNSTILE_SECRET_KEY.strip()
    token = (token or '').strip()
    if not token:
        return False

    payload = {
        'secret': secret,
        'response': token,
    }
    if remote_ip:
        payload['remoteip'] = remote_ip

    data = urllib.parse.urlencode(payload).encode()
    request = urllib.request.Request(
        TURNSTILE_VERIFY_URL,
        data=data,
        method='POST',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        logger.warning('Turnstile verification request failed: %s', exc)
        return False

    return body.get('success') is True

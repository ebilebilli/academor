from django.core.exceptions import ValidationError
from django.utils.translation import gettext

from projects.utils.turnstile import is_turnstile_configured, verify_turnstile_response


class TurnstileFormMixin:
    """Cloudflare Turnstile — POST field ``cf-turnstile-response``."""

    def __init__(self, *args, request=None, **kwargs):
        self._request = request
        super().__init__(*args, **kwargs)

    def turnstile_required(self):
        return is_turnstile_configured()

    def clean(self):
        cleaned_data = super().clean()
        if not self.turnstile_required():
            return cleaned_data

        token = (self.data.get('cf-turnstile-response') or '').strip()
        remote_ip = None
        if self._request is not None:
            remote_ip = self._request.META.get('REMOTE_ADDR')

        if not verify_turnstile_response(token, remote_ip):
            raise ValidationError(
                gettext('Please complete the security check.'),
                code='turnstile',
            )
        return cleaned_data

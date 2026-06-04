from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from projects.forms.turnstile_mixin import TurnstileFormMixin
from projects.utils.normalize_phone_number import validate_phone_number
from projects.utils.turnstile import is_turnstile_configured

_FIELD_CLASS = 'form-control form-control-sm'


class CoursePaymentForm(TurnstileFormMixin, forms.Form):
    buyer_name = forms.CharField(
        max_length=255,
        required=True,
        label=_('Full name'),
        widget=forms.TextInput(
            attrs={
                'class': _FIELD_CLASS,
                'autocomplete': 'name',
            }
        ),
    )
    buyer_email = forms.EmailField(
        max_length=254,
        required=False,
        label=_('Email address'),
        widget=forms.EmailInput(
            attrs={
                'class': _FIELD_CLASS,
                'autocomplete': 'email',
            }
        ),
    )
    buyer_phone = forms.CharField(
        max_length=30,
        required=False,
        label=_('Phone number'),
        widget=forms.TextInput(
            attrs={
                'class': _FIELD_CLASS,
                'autocomplete': 'tel',
            }
        ),
    )
    price_package_id = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)

    def turnstile_required(self):
        return bool(
            getattr(settings, 'PAYMENT_TURNSTILE_ENABLED', False)
            and is_turnstile_configured()
        )

    def clean(self):
        cleaned_data = super().clean()
        email = (cleaned_data.get('buyer_email') or '').strip()
        phone = (cleaned_data.get('buyer_phone') or '').strip()
        if not email and not phone:
            msg = _('Please provide an email address or phone number.')
            self.add_error('buyer_email', msg)
            self.add_error('buyer_phone', msg)
        cleaned_data['buyer_email'] = email
        cleaned_data['buyer_phone'] = phone
        return cleaned_data

    def clean_buyer_name(self):
        value = (self.cleaned_data.get('buyer_name') or '').strip()
        if not value:
            raise ValidationError(_('Full name is required.'))
        return value

    def clean_price_package_id(self):
        value = self.cleaned_data.get('price_package_id')
        if value is None:
            raise ValidationError(_('Please select a price package.'))
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValidationError(_('Invalid price package.'))

    def clean_buyer_email(self):
        return (self.cleaned_data.get('buyer_email') or '').strip()

    def clean_buyer_phone(self):
        value = (self.cleaned_data.get('buyer_phone') or '').strip()
        if value and not validate_phone_number(value):
            raise ValidationError(_('Please enter a valid phone number.'))
        return value

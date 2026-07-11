from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from projects.utils.normalize_phone_number import validate_phone_number

from payments.contract import is_valid_contract_number

_FIELD_CLASS = 'form-control form-control-sm'


class CoursePaymentForm(forms.Form):
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
        required=True,
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
    accept_contract = forms.BooleanField(
        required=True,
        label=_('I have read and accept the training agreement.'),
        error_messages={
            'required': _('You must accept the training agreement to proceed.'),
        },
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input'},
        ),
    )
    contract_number = forms.CharField(
        max_length=32,
        required=True,
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, request=None, mock_checkout=False, **kwargs):
        self._request = request
        self._mock_checkout = mock_checkout
        super().__init__(*args, **kwargs)
        if mock_checkout:
            self.fields['accept_contract'].label = _('I have read and accept the agreement.')
            self.fields['accept_contract'].error_messages = {
                'required': _('You must accept the agreement to proceed.'),
            }

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
        value = (self.cleaned_data.get('buyer_email') or '').strip()
        return value or None

    def clean_buyer_phone(self):
        value = (self.cleaned_data.get('buyer_phone') or '').strip()
        if not value:
            raise ValidationError(_('Phone number is required.'))
        if not validate_phone_number(value):
            raise ValidationError(_('Please enter a valid phone number.'))
        return value

    def clean_contract_number(self):
        value = (self.cleaned_data.get('contract_number') or '').strip()
        if not value:
            raise ValidationError(_('Training agreement number is missing.'))
        if not is_valid_contract_number(value):
            raise ValidationError(_('Invalid training agreement number.'))
        return value

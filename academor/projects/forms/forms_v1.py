from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from projects.models import ContactInquiry, Review
from projects.utils.normalize_phone_number import validate_phone_number

# Bot honeypots: must stay empty (hidden inputs; tabindex -1 for keyboard users).
_HP = {'autocomplete': 'off', 'tabindex': '-1', 'aria-hidden': 'true'}

class AppealContactForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs=_HP),
        label='',
    )
    fax = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs=_HP),
        label='',
    )
    company = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs=_HP),
        label='',
    )
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Full name')
        }),
        required=True,
        label=_('Full name')
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email address')
        }),
        required=False,
        label=_('Email address')
    )
    mobile_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Mobile number')
        }),
        required=False,
        label=_('Mobile number'),
        max_length=30
    )
    subject = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Subject')
        }),
        required=True,
        label=_('Subject'),
        max_length=250
    )
    info = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'style': 'height: 150px',
            'placeholder': _('Your message')
        }),
        required=True,
        label=_('Your message'),
        max_length=500
    )

    class Meta:
        model = ContactInquiry
        fields = [
            'full_name',
            'email',
            'mobile_number',
            'subject',
            'info'
        ]

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError(_('Something went wrong. Please try again.'))
        return value

    def clean_fax(self):
        if self.cleaned_data.get('fax'):
            raise ValidationError(_('Something went wrong. Please try again.'))
        return ''

    def clean_company(self):
        if self.cleaned_data.get('company'):
            raise ValidationError(_('Something went wrong. Please try again.'))
        return ''

    def clean(self):
        cleaned_data = super().clean()
        email = (cleaned_data.get('email') or '').strip()
        mobile_number = (cleaned_data.get('mobile_number') or '').strip()

        if not email and not mobile_number:
            msg = _('Please provide either an email address or a mobile number.')
            self.add_error('email', msg)
            self.add_error('mobile_number', msg)

        return cleaned_data

    def clean_mobile_number(self):
        value = (self.cleaned_data.get('mobile_number') or '').strip()
        if value and not validate_phone_number(value):
            raise ValidationError(_('Düzgün nömrə daxil edin'))
        return value


class ReviewForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs=_HP),
        label='',
    )
    fax = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs=_HP),
        label='',
    )
    company = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs=_HP),
        label='',
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': _('Ad və soyad'),
                'autocomplete': 'name',
            }
        ),
        required=True,
        label=_('Ad və soyad'),
        max_length=120,
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Rəyiniz'),
                'style': 'min-height: 148px;',
            }
        ),
        required=True,
        label=_('Rəy'),
        max_length=1000,
    )

    class Meta:
        model = Review
        fields = ['name', 'message']

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError(_('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'))
        return value

    def clean_fax(self):
        if self.cleaned_data.get('fax'):
            raise ValidationError(_('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'))
        return ''

    def clean_company(self):
        if self.cleaned_data.get('company'):
            raise ValidationError(_('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'))
        return ''


class TestUserForm(forms.Form):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs=_HP),
        label='',
    )
    fax = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs=_HP),
        label='',
    )
    company = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs=_HP),
        label='',
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ad Soyad')}),
        label=_('Ad Soyad'),
        max_length=100,
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='',
        max_length=100,
    )
    number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nömrə')}),
        label=_('Nömrə'),
        max_length=30,
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email')}),
        label=_('Email'),
    )

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise ValidationError(_('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'))
        return ''

    def clean_fax(self):
        if self.cleaned_data.get('fax'):
            raise ValidationError(_('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'))
        return ''

    def clean_company(self):
        if self.cleaned_data.get('company'):
            raise ValidationError(_('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'))
        return ''

    def clean_number(self):
        value = (self.cleaned_data.get('number') or '').strip()
        if not validate_phone_number(value):
            raise ValidationError(_('Düzgün nömrə daxil edin'))
        return value

import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from projects.forms.turnstile_mixin import TurnstileFormMixin
from projects.models import ContactInquiry, Review, StudyAbroadApplication
from projects.utils.normalize_phone_number import (
    validate_az_mobile_phone,
    validate_phone_number,
)

# Bot honeypots: must stay empty (hidden inputs; tabindex -1).
_HP = {'autocomplete': 'off', 'tabindex': '-1', 'aria-hidden': 'true'}

class AppealContactForm(TurnstileFormMixin, forms.ModelForm):
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
        label=_('Email address'),
    )
    mobile_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Mobile number'),
            'autocomplete': 'tel',
        }),
        required=True,
        label=_('Mobile number'),
        max_length=30,
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

    def clean_email(self):
        value = (self.cleaned_data.get('email') or '').strip()
        return value or None

    def clean_mobile_number(self):
        value = (self.cleaned_data.get('mobile_number') or '').strip()
        if not value:
            raise ValidationError(_('Phone number is required.'))
        if not validate_phone_number(value):
            raise ValidationError(_('Please enter a valid phone number.'))
        return value


class ReviewForm(TurnstileFormMixin, forms.ModelForm):
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
    hp_address = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs=_HP),
        label='',
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Ad Soyad'),
                'autocomplete': 'name',
            }
        ),
        required=True,
        label=_('Ad Soyad'),
        max_length=120,
    )
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Mobile number'),
                'autocomplete': 'tel',
                'inputmode': 'tel',
            }
        ),
        required=True,
        label=_('Mobile number'),
        max_length=30,
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Your review'),
                'maxlength': '276',
            }
        ),
        required=True,
        label=_('Your review'),
        max_length=276,
    )
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=5,
        label=_('Star rating'),
        widget=forms.HiddenInput(
            attrs={'class': 'review-form-rating-input'},
        ),
    )

    class Meta:
        model = Review
        fields = ['name', 'phone', 'message', 'rating']

    def clean_phone(self):
        value = (self.cleaned_data.get('phone') or '').strip()
        if not value:
            raise ValidationError(_('Please enter your mobile number.'))
        if not validate_phone_number(value):
            raise ValidationError(_('Düzgün nömrə daxil edin'))
        return value

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

    def clean_hp_address(self):
        if self.cleaned_data.get('hp_address'):
            raise ValidationError(_('Something went wrong. Please try again.'))
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


class LuckyWheelPhoneForm(forms.Form):
    phone = forms.CharField(
        max_length=30,
        required=True,
        label=_('Mobile number'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Mobile number'),
                'autocomplete': 'tel',
                'inputmode': 'tel',
            }
        ),
    )

    def clean_phone(self):
        value = (self.cleaned_data.get('phone') or '').strip()
        if not value:
            raise ValidationError(_('Phone number is required.'))
        result = validate_az_mobile_phone(value)
        if not result['valid']:
            raise ValidationError(_('Please enter a valid phone number.'))
        return result['normalized']


# Letters in any script, single spaces / hyphens / apostrophes / dots between words.
_PERSON_NAME_RE = re.compile(r"^[^\W\d_]+(?:[\s'’.\-]+[^\W\d_]+)*\.?$")
# Country / major: free text, but must contain letters and no links.
_FREE_TEXT_RE = re.compile(r"^[\w\s'’.,&/()+\-]+$")
_LINK_RE = re.compile(r'(https?://|www\.)', re.IGNORECASE)


class StudyAbroadApplicationForm(TurnstileFormMixin, forms.ModelForm):
    """Study-abroad consultation request (abroad page + compact homepage form)."""

    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs=_HP),
        label='',
    )

    class Meta:
        model = StudyAbroadApplication
        fields = [
            'full_name',
            'phone_number',
            'consultation_format',
            'study_level',
            'desired_country',
            'desired_major',
            'scholarship_importance',
            'tuition_budget',
            'international_certificates',
        ]
        labels = {
            'full_name': _('Ad və soyad'),
            'phone_number': _('Əlaqə nömrəsi'),
            'consultation_format': _('İlkin konsultasiyanın formatı'),
            'study_level': _('Təhsil səviyyəsi'),
            'desired_country': _('Təhsil almaq istədiyiniz ölkə'),
            'desired_major': _('Təhsil almaq istədiyiniz ixtisas'),
            'scholarship_importance': _('Təqaüdün əhəmiyyəti'),
            'tuition_budget': _('Təhsil haqqı üçün büdcə'),
            'international_certificates': _('Beynəlxalq sertifikatlar'),
        }
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Məs.: Aysel Məmmədova'),
                'autocomplete': 'name',
                'maxlength': '120',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('+994 50 123 45 67'),
                'autocomplete': 'tel',
                'inputmode': 'tel',
                'maxlength': '30',
            }),
            'consultation_format': forms.Select(attrs={'class': 'form-select'}),
            'study_level': forms.Select(attrs={'class': 'form-select'}),
            'desired_country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Məs.: Almaniya, Kanada'),
                'maxlength': '100',
            }),
            'desired_major': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Məs.: Kompüter elmləri'),
                'maxlength': '150',
            }),
            'scholarship_importance': forms.Select(attrs={'class': 'form-select'}),
            'tuition_budget': forms.Select(attrs={'class': 'form-select'}),
            'international_certificates': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Məs.: IELTS 7.0, SAT 1400 (yoxdursa boş saxlayın)'),
                'maxlength': '1000',
            }),
        }

    SELECT_PLACEHOLDER = _('Seçin')
    # compact (homepage) form: labels are hidden, so short names go in the placeholders
    COMPACT_LABELS = {
        'full_name': _('Ad və soyad'),
        'phone_number': _('Əlaqə nömrəsi'),
        'desired_country': _('Ölkə'),
        'desired_major': _('İxtisas'),
        'study_level': _('Təhsil səviyyəsi'),
        'consultation_format': _('Konsultasiya formatı'),
        'scholarship_importance': _('Təqaüd'),
        'tuition_budget': _('Büdcə'),
    }

    def __init__(self, *args, compact=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.compact = compact
        self.fields['international_certificates'].required = False
        for name in ('consultation_format', 'study_level', 'scholarship_importance', 'tuition_budget'):
            field = self.fields[name]
            field.required = True
            # compact (homepage) form hides labels, so the empty option names the field
            empty = self.COMPACT_LABELS[name] if compact else self.SELECT_PLACEHOLDER
            field.choices = [('', empty)] + [c for c in field.choices if c[0] != '']
        if compact:
            for name in ('full_name', 'phone_number', 'desired_country', 'desired_major'):
                self.fields[name].widget.attrs['placeholder'] = self.COMPACT_LABELS[name]
        for name in self.Meta.fields:
            if name == 'international_certificates':
                continue
            self.fields[name].required = True
            self.fields[name].widget.attrs['required'] = 'required'
            self.fields[name].widget.attrs['aria-required'] = 'true'

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise ValidationError(_('Something went wrong. Please try again.'))
        return ''

    def clean_full_name(self):
        value = ' '.join((self.cleaned_data.get('full_name') or '').split())
        if len(value) < 3 or ' ' not in value:
            raise ValidationError(_('Ad və soyadınızı tam daxil edin.'))
        if not _PERSON_NAME_RE.fullmatch(value):
            raise ValidationError(_('Ad və soyad yalnız hərflərdən ibarət olmalıdır.'))
        return value

    def clean_phone_number(self):
        value = (self.cleaned_data.get('phone_number') or '').strip()
        if not validate_phone_number(value):
            raise ValidationError(_('Düzgün nömrə daxil edin'))
        return value

    def _clean_free_text(self, name, min_length=2):
        value = ' '.join((self.cleaned_data.get(name) or '').split())
        if len(value) < min_length or not any(ch.isalpha() for ch in value):
            raise ValidationError(_('Bu sahəni düzgün doldurun.'))
        if _LINK_RE.search(value) or not _FREE_TEXT_RE.fullmatch(value):
            raise ValidationError(_('Yalnız hərf, rəqəm və sadə durğu işarələrindən istifadə edin.'))
        return value

    def clean_desired_country(self):
        return self._clean_free_text('desired_country')

    def clean_desired_major(self):
        return self._clean_free_text('desired_major')

    def clean_international_certificates(self):
        value = (self.cleaned_data.get('international_certificates') or '').strip()
        if _LINK_RE.search(value):
            raise ValidationError(_('Linklər qəbul edilmir.'))
        return value

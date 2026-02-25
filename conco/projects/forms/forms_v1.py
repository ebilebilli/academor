from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from projects.models import AppealVacancy, AppealContact


class AppealForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='',
    )
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ad Soyad')
        }),
        required=True,
        label=_('Ad Soyad')
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nümunə: example@email.com')
        }),
        required=True,
        label=_('E-poçt')
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nümunə: 0501234567')
        }),
        required=True,
        label=_('Mobil Nömrə')
    )
    info = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Əlavə məlumat')
        }),
        required=False,
        label=_('Əlavə məlumat'),
        max_length=250
    )
    cv = forms.FileField(
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.doc,.docx',
            'class': 'form-control'
        }),
        required=True,
        label=_('CV faylı')
    )

    class Meta:
        model = AppealVacancy
        fields = [
            'full_name',
            'email',
            'phone_number',
            'info',
            'cv'
        ]

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError(_('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'))
        return value


class AppealContactForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='',
    )
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ad soyad')
        }),
        required=True,
        label=_('Ad soyad')
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('E-poçt ünvanı')
        }),
        required=True,
        label=_('E-poçt ünvanı')
    )
    subject = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Subyekt')
        }),
        required=True,
        label=_('Subyekt'),
        max_length=250
    )
    info = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': _('Mesajınız')
        }),
        required=True,
        label=_('Mesajınız'),
        max_length=500
    )

    class Meta:
        model = AppealContact
        fields = [
            'full_name',
            'email',
            'subject',
            'info'
        ]

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError(_('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'))
        return value

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from projects.models import JobApplication, ContactInquiry, Review


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
        model = JobApplication
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
        required=True,
        label=_('Email address')
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
            'subject',
            'info'
        ]

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError(_('Something went wrong. Please try again.'))
        return value


class ReviewForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='',
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ad')
        }),
        required=True,
        label=_('Ad'),
        max_length=120,
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Rəyiniz')
        }),
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


class TestUserForm(forms.Form):
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

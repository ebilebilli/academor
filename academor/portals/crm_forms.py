from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from portals.models import Lead, LeadActivity, StudentCharge, StudentPayment, StudentProfile


class CrmFormMixin:
    """Give every widget the CRM input class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            css = 'crm-input'
            if isinstance(widget, forms.Select):
                css = 'crm-input crm-select'
            elif isinstance(widget, forms.Textarea):
                css = 'crm-input crm-textarea'
            widget.attrs.setdefault('class', css)


def staff_users():
    return get_user_model().objects.filter(is_staff=True, is_active=True).order_by('username')


class LeadForm(CrmFormMixin, forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            'full_name', 'phone', 'email', 'source', 'interest', 'level', 'status', 'assigned_to',
            'next_action_at', 'trial_at', 'message', 'lost_reason',
        )
        widgets = {
            'next_action_at': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'trial_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = staff_users()
        self.fields['assigned_to'].label_from_instance = lambda u: u.get_full_name() or u.username


class LeadNoteForm(CrmFormMixin, forms.ModelForm):
    class Meta:
        model = LeadActivity
        fields = ('kind', 'text')
        widgets = {'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Zəngin nəticəsi, razılaşma, qeyd…'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kind'].choices = [
            (k, v) for k, v in LeadActivity.Kind.choices if k in ('note', 'call', 'message')
        ]
        self.fields['text'].required = True


class StudentChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        phone = f' · {obj.phone}' if getattr(obj, 'phone', '') else ''
        return f'{obj.full_name}{phone}'


class PaymentForm(CrmFormMixin, forms.ModelForm):
    student = StudentChoiceField(
        queryset=StudentProfile.objects.select_related('user').order_by('user__username'), label='Tələbə',
    )

    class Meta:
        model = StudentPayment
        fields = ('student', 'amount', 'method', 'paid_at', 'payer', 'note')
        widgets = {
            'paid_at': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paid_at'].initial = timezone.localdate()

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount is None or amount <= 0:
            raise forms.ValidationError('Məbləğ sıfırdan böyük olmalıdır.')
        return amount


class ChargeForm(CrmFormMixin, forms.ModelForm):
    student = StudentChoiceField(
        queryset=StudentProfile.objects.select_related('user').order_by('user__username'), label='Tələbə',
    )

    class Meta:
        model = StudentCharge
        fields = ('student', 'kind', 'group', 'description', 'amount', 'due_date')
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].initial = timezone.localdate()
        self.fields['kind'].initial = StudentCharge.Kind.PACKAGE

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount is None or amount <= 0:
            raise forms.ValidationError('Məbləğ sıfırdan böyük olmalıdır.')
        return amount

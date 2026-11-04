import secrets

from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from portals.models import (
    Enrollment,
    Lead,
    LeadActivity,
    Schedule,
    StudentCharge,
    StudentPayment,
    StudentProfile,
    StudyGroup,
    TeacherProfile,
)
from portals.utils.normalize_phone_number import phone_number_validator

User = get_user_model()

DATE = {'type': 'date'}


def plain_number(value):
    """Decimal('1100.00') → '1100', Decimal('32.200') → '32.2'."""
    from decimal import Decimal

    if isinstance(value, Decimal):
        text = f'{value.normalize():f}'
        return text
    return value


class NumberInput(forms.NumberInput):
    def format_value(self, value):
        return super().format_value(plain_number(value))
MONEY = {'step': '0.01', 'min': '0', 'placeholder': '0.00', 'inputmode': 'decimal'}
WEEKDAYS = [(0, 'B.e.'), (1, 'Ç.a.'), (2, 'Çər.'), (3, 'C.a.'), (4, 'Cümə'), (5, 'Şən.'), (6, 'Baz.')]


class CrmFormMixin:
    """Give every widget the CRM input class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                continue
            css = 'crm-input'
            if isinstance(widget, forms.Select):
                css = 'crm-input crm-select'
            elif isinstance(widget, forms.Textarea):
                css = 'crm-input crm-textarea'
            widget.attrs.setdefault('class', css)


def staff_users():
    return User.objects.filter(is_staff=True, is_active=True).order_by('username')


def unique_username(full_name):
    """Portal usernames are the person's name (as the existing import does); add a number on clashes."""
    base = ' '.join((full_name or '').split())[:140] or 'tələbə'
    name, n = base, 2
    while User.objects.filter(username__iexact=name).exists():
        name = f'{base} {n}'
        n += 1
    return name


def new_portal_user(full_name):
    user = User(username=unique_username(full_name))
    user.set_unusable_password()  # a password is generated on the student's page when needed
    user.save()
    return user


def new_password():
    return secrets.token_urlsafe(6).replace('-', 'x').replace('_', 'y')


class PersonChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        phone = f' · {obj.phone}' if getattr(obj, 'phone', '') else ''
        return f'{obj.full_name}{phone}'


class TeacherChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.full_name


StudentChoiceField = PersonChoiceField


def teachers_qs():
    return TeacherProfile.objects.select_related('user').order_by('user__username')


def groups_qs():
    return StudyGroup.objects.filter(is_register_only=False, is_main_register=False).order_by('-is_active', 'name')


# ---------------------------------------------------------------- leads
class LeadForm(CrmFormMixin, forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            'full_name', 'phone', 'email', 'source', 'interest', 'level', 'status', 'assigned_to',
            'next_action_at', 'trial_at', 'message', 'lost_reason',
        )
        widgets = {
            'next_action_at': forms.DateInput(attrs=DATE, format='%Y-%m-%d'),
            'trial_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'message': forms.Textarea(attrs={'rows': 3}),
            'interest': forms.TextInput(attrs={'list': 'crm-courses'}),
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


# ---------------------------------------------------------------- students & courses
class EnrollmentForm(CrmFormMixin, forms.ModelForm):
    teacher = TeacherChoiceField(queryset=teachers_qs(), required=False, label='Müəllim')

    class Meta:
        model = Enrollment
        fields = (
            'course', 'group', 'teacher', 'monthly_fee', 'teacher_percent', 'start_date', 'first_due_date',
            'status', 'ended_at', 'leave_reason', 'note',
        )
        widgets = {
            'course': forms.TextInput(attrs={'list': 'crm-courses', 'placeholder': 'General English, IELTS, FMVA…'}),
            'monthly_fee': NumberInput(attrs=MONEY),
            'teacher_percent': NumberInput(attrs={'step': 'any', 'min': '0', 'max': '100', 'placeholder': '50'}),
            'start_date': forms.DateInput(attrs=DATE, format='%Y-%m-%d'),
            'first_due_date': forms.DateInput(attrs=DATE, format='%Y-%m-%d'),
            'ended_at': forms.DateInput(attrs=DATE, format='%Y-%m-%d'),
        }
        labels = {'monthly_fee': 'Aylıq haqq (AZN)', 'teacher_percent': 'Müəllim faizi (%)'}

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student or (self.instance.student if self.instance.pk else None)
        self.initial_group_id = self.instance.group_id
        self.fields['group'].queryset = groups_qs().select_related('teacher__user')
        self.fields['group'].required = False
        self.fields['first_due_date'].help_text = 'Hər ay bu günə hesab yazılır. Boşdursa — başlama tarixi.'
        if not self.instance.pk:
            self.fields['start_date'].initial = timezone.localdate()

    def group_teachers_json(self):
        import json

        return json.dumps({str(g.pk): g.teacher_id for g in self.fields['group'].queryset})

    def clean_monthly_fee(self):
        fee = self.cleaned_data.get('monthly_fee')
        if fee is not None and fee < 0:
            raise forms.ValidationError('Məbləğ mənfi ola bilməz.')
        return fee or 0

    def clean_teacher_percent(self):
        pct = self.cleaned_data.get('teacher_percent') or 0
        if pct < 0 or pct > 100:
            raise forms.ValidationError('Faiz 0 ilə 100 arasında olmalıdır.')
        return pct

    def clean(self):
        data = super().clean()
        group, status = data.get('group'), data.get('status')
        if group and not data.get('teacher'):
            data['teacher'] = group.teacher
        if status in (Enrollment.Status.LEFT, Enrollment.Status.FINISHED) and not data.get('ended_at'):
            data['ended_at'] = timezone.localdate()
        if status in (Enrollment.Status.ACTIVE, Enrollment.Status.WAITING):
            data['ended_at'] = None
        if group and status == Enrollment.Status.ACTIVE and group.max_students:
            already = self.student and group.students.filter(pk=self.student.pk).exists()
            if not already and group.students.count() >= group.max_students:
                self.add_error('group', f'Qrup doludur ({group.max_students} yer). Maksimumu qrup səhifəsində artırın.')
        return data


class StudentForm(CrmFormMixin, forms.Form):
    full_name = forms.CharField(label='Ad, soyad', max_length=140)
    phone = forms.CharField(label='Telefon', max_length=30, required=False, validators=[phone_number_validator])
    birth_date = forms.DateField(label='Doğum tarixi', required=False, widget=forms.DateInput(attrs=DATE, format='%Y-%m-%d'))
    email = forms.EmailField(label='E-poçt', required=False)

    def __init__(self, *args, student=None, **kwargs):
        self.student = student
        if student and 'initial' not in kwargs:
            kwargs['initial'] = {
                'full_name': student.full_name, 'phone': student.phone,
                'birth_date': student.birth_date, 'email': student.user.email,
            }
        super().__init__(*args, **kwargs)

    def clean_full_name(self):
        name = ' '.join(self.cleaned_data['full_name'].split())
        clash = User.objects.filter(username__iexact=name)
        if self.student:
            clash = clash.exclude(pk=self.student.user_id)
        if self.student and clash.exists():
            raise forms.ValidationError('Bu adda başqa istifadəçi var — fərqləndirin (məs. ikinci ad və ya rəqəm).')
        return name

    @transaction.atomic
    def save(self):
        d = self.cleaned_data
        if self.student:
            st = self.student
            user = st.user
            user.username, user.email = d['full_name'], d['email'] or ''
            user.save(update_fields=['username', 'email'])
        else:
            user = new_portal_user(d['full_name'])
            user.email = d['email'] or ''
            user.save(update_fields=['email'])
            st = StudentProfile(user=user)
        st.phone, st.birth_date = d['phone'] or '', d['birth_date']
        if not st.enrollment_date:
            st.enrollment_date = timezone.localdate()
        st.save()
        return st


def save_enrollment(form, student, user=None, lead=None):
    """Save an enrollment and keep the group membership (portal, attendance) in step with it."""
    from portals.utils import crm

    old_group_id = form.initial_group_id
    e = form.save(commit=False)
    e.student = student
    if not e.pk:
        e.created_by, e.lead = user, lead
    e.teacher = form.cleaned_data.get('teacher')
    e.ended_at = form.cleaned_data.get('ended_at')
    e.save()
    in_group = e.status == Enrollment.Status.ACTIVE
    if old_group_id and old_group_id != e.group_id:
        still = Enrollment.objects.filter(student=student, group_id=old_group_id, status=Enrollment.Status.ACTIVE)
        if not still.exists():
            StudyGroup.objects.get(pk=old_group_id).students.remove(student)
    if e.group_id:
        if in_group:
            e.group.students.add(student)
        elif not Enrollment.objects.filter(
            student=student, group_id=e.group_id, status=Enrollment.Status.ACTIVE,
        ).exclude(pk=e.pk).exists():
            e.group.students.remove(student)
    if e.status in (Enrollment.Status.LEFT, Enrollment.Status.FINISHED):
        crm.close_enrollment_billing(e)
    return e


# ---------------------------------------------------------------- money
class PaymentForm(CrmFormMixin, forms.ModelForm):
    student = PersonChoiceField(
        queryset=StudentProfile.objects.select_related('user').order_by('user__username'), label='Tələbə',
    )
    enrollment = forms.ModelChoiceField(
        queryset=Enrollment.objects.select_related('teacher__user').order_by('course'), required=False,
        label='Kurs', empty_label='— Birdəfəlik ödəniş (kurssuz) —',
    )
    teacher = TeacherChoiceField(queryset=teachers_qs(), required=False, label='Müəllim')

    class Meta:
        model = StudentPayment
        fields = (
            'student', 'enrollment', 'course', 'amount', 'method', 'paid_at', 'teacher', 'teacher_percent',
            'is_new_customer', 'payer', 'note',
        )
        widgets = {
            'paid_at': forms.DateInput(attrs=DATE, format='%Y-%m-%d'),
            'amount': NumberInput(attrs={**MONEY, 'min': '0.01'}),
            'teacher_percent': NumberInput(attrs={'step': 'any', 'min': '0', 'max': '100'}),
            'course': forms.TextInput(attrs={'list': 'crm-courses', 'placeholder': 'məs. IELTS Mock test'}),
            'note': forms.TextInput(attrs={'placeholder': 'Müqavilə bağlandı, 10% endirim…'}),
        }
        labels = {'course': 'Kurs adı (birdəfəlik)', 'teacher_percent': 'Müəllim faizi (%)'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paid_at'].initial = timezone.localdate()
        self.fields['teacher_percent'].required = False
        self.fields['course'].required = False
        self.fields['enrollment'].label_from_instance = self._enrollment_label

    @staticmethod
    def _enrollment_label(e):
        bits = [e.course]
        if e.teacher_id:
            bits.append(e.teacher.full_name)
        if e.monthly_fee:
            bits.append(f'{plain_number(e.monthly_fee)} AZN/ay')
        return ' · '.join(bits)

    def enrollment_options(self):
        """data-* for the course <select>, so the form fills itself in when a course is picked."""
        return [
            {'pk': e.pk, 'student': e.student_id, 'fee': plain_number(e.monthly_fee), 'teacher': e.teacher_id or '',
             'pct': plain_number(e.teacher_percent), 'course': e.course, 'label': self._enrollment_label(e),
             'inactive': e.status not in (Enrollment.Status.ACTIVE, Enrollment.Status.WAITING)}
            for e in self.fields['enrollment'].queryset
        ]

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount is None or amount <= 0:
            raise forms.ValidationError('Məbləğ sıfırdan böyük olmalıdır.')
        return amount

    def clean(self):
        data = super().clean()
        st, e = data.get('student'), data.get('enrollment')
        if e and st and e.student_id != st.pk:
            self.add_error('enrollment', 'Bu kurs seçilmiş tələbəyə aid deyil.')
            return data
        if e:
            data['course'] = e.course
            if not data.get('teacher'):
                data['teacher'] = e.teacher
            if data.get('teacher_percent') in (None, ''):
                data['teacher_percent'] = e.teacher_percent
        elif not (data.get('course') or '').strip():
            self.add_error('course', 'Kurs seçin və ya birdəfəlik ödənişin adını yazın.')
        pct = data.get('teacher_percent') or 0
        if pct < 0 or pct > 100:
            self.add_error('teacher_percent', 'Faiz 0 ilə 100 arasında olmalıdır.')
        data['teacher_percent'] = pct
        return data

    def save(self, commit=True):
        pay = super().save(commit=False)
        pay.course = self.cleaned_data.get('course') or ''
        pay.teacher = self.cleaned_data.get('teacher')
        pay.teacher_percent = self.cleaned_data.get('teacher_percent') or 0
        money_changed = not pay.pk or {'amount', 'teacher', 'teacher_percent', 'enrollment'} & set(self.changed_data)
        if money_changed and pay.teacher_status != StudentPayment.TeacherStatus.PAID:
            pay.teacher_status = StudentPayment.TeacherStatus.PENDING
            pay.apply_teacher_share()
        if commit:
            pay.save()
        return pay


class ChargeForm(CrmFormMixin, forms.ModelForm):
    student = PersonChoiceField(
        queryset=StudentProfile.objects.select_related('user').order_by('user__username'), label='Tələbə',
    )

    class Meta:
        model = StudentCharge
        fields = ('student', 'kind', 'enrollment', 'description', 'amount', 'due_date')
        widgets = {
            'due_date': forms.DateInput(attrs=DATE, format='%Y-%m-%d'),
            'amount': NumberInput(attrs={**MONEY, 'min': '0.01'}),
        }
        labels = {'enrollment': 'Kurs (istəyə görə)'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].initial = timezone.localdate()
        self.fields['kind'].initial = StudentCharge.Kind.PACKAGE
        self.fields['kind'].choices = [c for c in StudentCharge.Kind.choices if c[0] != StudentCharge.Kind.MONTHLY]
        self.fields['enrollment'].queryset = Enrollment.objects.order_by('course')
        self.fields['enrollment'].label_from_instance = lambda e: e.course

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount is None or amount <= 0:
            raise forms.ValidationError('Məbləğ sıfırdan böyük olmalıdır.')
        return amount

    def clean(self):
        data = super().clean()
        st, e = data.get('student'), data.get('enrollment')
        if e and st and e.student_id != st.pk:
            self.add_error('enrollment', 'Bu kurs seçilmiş tələbəyə aid deyil.')
        return data


# ---------------------------------------------------------------- teachers & groups
class TeacherForm(CrmFormMixin, forms.Form):
    full_name = forms.CharField(label='Ad, soyad', max_length=140)
    phone = forms.CharField(label='Telefon', max_length=30, required=False, validators=[phone_number_validator])
    specialization = forms.CharField(label='Fənn(lər)', max_length=200, required=False,
                                     widget=forms.TextInput(attrs={'placeholder': 'IELTS, General English…'}))

    def clean_full_name(self):
        return ' '.join(self.cleaned_data['full_name'].split())

    @transaction.atomic
    def save(self):
        d = self.cleaned_data
        user = new_portal_user(d['full_name'])
        return TeacherProfile.objects.create(user=user, phone=d['phone'] or '', specialization=d['specialization'] or '')


class GroupForm(CrmFormMixin, forms.ModelForm):
    teacher = TeacherChoiceField(queryset=teachers_qs(), label='Müəllim')
    days = forms.TypedMultipleChoiceField(
        choices=WEEKDAYS, coerce=int, required=False, widget=forms.CheckboxSelectMultiple, label='Dərs günləri',
    )
    start_time = forms.TimeField(label='Saat', required=False, widget=forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'))
    duration_min = forms.IntegerField(label='Müddət (dəq)', required=False, min_value=15, max_value=300, initial=90)
    room_or_link = forms.CharField(label='Otaq / link', required=False, max_length=500)

    class Meta:
        model = StudyGroup
        fields = ('name', 'teacher', 'max_students', 'start_date', 'is_active')
        widgets = {'start_date': forms.DateInput(attrs=DATE, format='%Y-%m-%d')}
        labels = {'name': 'Qrupun adı', 'max_students': 'Maksimum tələbə', 'start_date': 'Başlama', 'is_active': 'Aktiv'}

    def clean(self):
        data = super().clean()
        if data.get('days') and not data.get('start_time'):
            self.add_error('start_time', 'Dərs saatını yazın.')
        return data

    @transaction.atomic
    def save(self, commit=True):
        group = super().save(commit=True)
        d = self.cleaned_data
        existing = set(group.schedules.values_list('weekday', 'start_time'))
        for day in d.get('days') or []:
            if (day, d['start_time']) in existing:
                continue
            Schedule.objects.create(
                group=group, weekday=day, start_time=d['start_time'], duration_min=d.get('duration_min') or 90,
                room_or_link=d.get('room_or_link') or '', effective_from=group.start_date or timezone.localdate(),
            )
        return group

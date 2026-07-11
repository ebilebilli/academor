from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from portals.models import CustomerProfile, ParentProfile, StudentProfile, TeacherProfile, TeacherCourseSpecialization
from portals.utils.normalize_phone_number import phone_number_validator
from portals.utils.portal_services import get_active_course_type_choices
from portals.utils.teacher_courses import validate_teacher_course_codes
from portals.utils.username_validators import portal_username_validator

User = get_user_model()

PORTAL_ROLE_TEACHER = 'teacher'
PORTAL_ROLE_STUDENT = 'student'
PORTAL_ROLE_PARENT = 'parent'
PORTAL_ROLE_CUSTOMER = 'customer'
PORTAL_ROLE_STAFF = 'staff'
PORTAL_ROLE_ADMIN = 'admin'

PORTAL_ROLE_CHOICES = (
    (PORTAL_ROLE_TEACHER, _('Teacher')),
    (PORTAL_ROLE_STUDENT, _('Student')),
    (PORTAL_ROLE_PARENT, _('Parent')),
    (PORTAL_ROLE_CUSTOMER, _('Customer')),
    (PORTAL_ROLE_STAFF, _('Staff (Django admin only)')),
    (PORTAL_ROLE_ADMIN, _('Admin (Django admin only)')),
)

PORTAL_PROFILE_ROLES = {
    PORTAL_ROLE_TEACHER,
    PORTAL_ROLE_STUDENT,
    PORTAL_ROLE_PARENT,
    PORTAL_ROLE_CUSTOMER,
}


def get_user_portal_role(user) -> str | None:
    if not user or not user.pk:
        return None
    if user.is_superuser:
        return PORTAL_ROLE_ADMIN
    if TeacherProfile.objects.filter(user_id=user.pk).exists():
        return PORTAL_ROLE_TEACHER
    if StudentProfile.objects.filter(user_id=user.pk).exists():
        return PORTAL_ROLE_STUDENT
    if ParentProfile.objects.filter(user_id=user.pk).exists():
        return PORTAL_ROLE_PARENT
    if CustomerProfile.objects.filter(user_id=user.pk).exists():
        return PORTAL_ROLE_CUSTOMER
    if user.is_staff:
        return PORTAL_ROLE_STAFF
    return None


def set_teacher_course_specializations(teacher_profile, course_codes):
    codes = validate_teacher_course_codes([code for code in (course_codes or []) if code])
    TeacherCourseSpecialization.objects.filter(teacher=teacher_profile).exclude(
        course_type__in=codes,
    ).delete()
    existing = set(teacher_profile.get_course_type_codes())
    for code in codes:
        if code not in existing:
            TeacherCourseSpecialization.objects.create(
                teacher=teacher_profile,
                course_type=code,
            )
    from portals.utils.teacher_courses import sync_teacher_specialization_text

    sync_teacher_specialization_text(teacher_profile.pk)


def create_portal_profile(user, role, phone='', students=None, teacher_courses=None, mock_credits=None, customer_teacher=None):
    if role == PORTAL_ROLE_ADMIN:
        user.is_staff = True
        user.is_superuser = True
    elif role == PORTAL_ROLE_STAFF:
        user.is_staff = True
        user.is_superuser = False
    else:
        user.is_staff = False
        user.is_superuser = False

    user.save(update_fields=['is_staff', 'is_superuser'])

    if role == PORTAL_ROLE_TEACHER:
        profile = TeacherProfile.objects.create(
            user=user,
            phone=phone,
        )
        if teacher_courses:
            set_teacher_course_specializations(profile, teacher_courses)
    elif role == PORTAL_ROLE_STUDENT:
        StudentProfile.objects.create(
            user=user,
            phone=phone,
        )
    elif role == PORTAL_ROLE_PARENT:
        profile = ParentProfile.objects.create(
            user=user,
            phone=phone,
        )
        if students:
            profile.students.set(students)
    elif role == PORTAL_ROLE_CUSTOMER:
        credits = 1 if mock_credits is None else max(0, int(mock_credits))
        CustomerProfile.objects.create(
            user=user,
            phone=phone,
            ielts_mock_credits=credits,
            sat_mock_credits=0,
            teacher=customer_teacher,
        )


class PortalLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label=_('Username'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'username',
                'placeholder': _('Username'),
            },
        ),
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'current-password',
                'placeholder': _('Password'),
            },
        ),
    )
    next = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    def clean_username(self):
        return (self.cleaned_data.get('username') or '').strip()


class PortalUserCreationForm(UserCreationForm):
    portal_role = forms.ChoiceField(
        label=_('Role'),
        choices=PORTAL_ROLE_CHOICES,
        initial=PORTAL_ROLE_STUDENT,
        help_text=_('Portal role and admin access for this account.'),
    )
    phone = forms.CharField(
        label=_('Phone'),
        max_length=30,
        required=False,
        validators=[phone_number_validator],
        help_text=_('Optional. Example: +994501234567 or 0501234567.'),
    )
    linked_students = forms.ModelMultipleChoiceField(
        label=_('Linked students'),
        queryset=StudentProfile.objects.select_related('user').order_by('user__username', 'id'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 8}),
        help_text=_('Required when role is Parent. Select one or more children.'),
    )
    teacher_courses = forms.MultipleChoiceField(
        label=_('Course specializations'),
        choices=(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text=_('Required for teachers. Pick every active site service this teacher may teach.'),
    )
    mock_credits = forms.IntegerField(
        label=_('Initial mock credits'),
        required=False,
        min_value=0,
        initial=1,
        help_text=_('For Customer role only. Defaults to 1 mock test credit.'),
    )
    assigned_teacher = forms.ModelChoiceField(
        label=_('Reviewing teacher'),
        queryset=TeacherProfile.objects.select_related('user').order_by('user__username', 'id'),
        required=False,
        help_text=_('For Customer role only. Teacher who will review mock Writing and Speaking.'),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher_courses'].choices = get_active_course_type_choices()
        if 'username' in self.fields:
            self.fields['username'].validators = [portal_username_validator]
        visible_password_attrs = {
            'class': 'vTextField portal-visible-password',
            'autocomplete': 'new-password',
            'spellcheck': 'false',
            'data-generate-label': str(_('Generate random password')),
            'data-generated-label': str(_('Generated password')),
        }
        if 'password1' in self.fields:
            self.fields['password1'].widget = forms.TextInput(attrs=visible_password_attrs)
            self.fields['password1'].help_text = _(
                'Shown in plain text so you can copy it for the user. '
                'Use "Generate random password" below.'
            )
        if 'password2' in self.fields:
            self.fields['password2'].widget = forms.TextInput(attrs=visible_password_attrs)
            self.fields['password2'].label = _('Password (confirm)')

    class Media:
        js = ('portals/admin/js/user_password_generator.js',)
        css = {'all': ('portals/css/portal-admin.css',)}

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('portal_role')

        if role == PORTAL_ROLE_PARENT and not cleaned.get('linked_students'):
            self.add_error('linked_students', _('Select at least one linked student.'))

        if role == PORTAL_ROLE_TEACHER and not cleaned.get('teacher_courses'):
            self.add_error('teacher_courses', _('Select at least one course specialization.'))

        if role == PORTAL_ROLE_CUSTOMER and not cleaned.get('assigned_teacher'):
            self.add_error('assigned_teacher', _('Select the teacher who will review this customer\'s mock tests.'))

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data['portal_role']
        phone = (self.cleaned_data.get('phone') or '').strip()
        students = self.cleaned_data.get('linked_students')

        if not commit:
            return user

        user.save()

        if role in PORTAL_PROFILE_ROLES:
            raw_credits = self.cleaned_data.get('mock_credits')
            profile_credits = (
                (1 if raw_credits in (None, '') else raw_credits)
                if role == PORTAL_ROLE_CUSTOMER
                else (raw_credits or 0)
            )
            create_portal_profile(
                user,
                role,
                phone=phone,
                students=students,
                teacher_courses=self.cleaned_data.get('teacher_courses'),
                mock_credits=profile_credits,
                customer_teacher=self.cleaned_data.get('assigned_teacher'),
            )
        else:
            if role == PORTAL_ROLE_ADMIN:
                user.is_staff = True
                user.is_superuser = True
            elif role == PORTAL_ROLE_STAFF:
                user.is_staff = True
                user.is_superuser = False
            user.save(update_fields=['is_staff', 'is_superuser'])

        return user


class PortalUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].validators = [portal_username_validator]


_PROFILE_WIDGETS = {
    'profile_image': forms.FileInput(
        attrs={'class': 'visually-hidden', 'accept': 'image/*', 'id': 'id_profile_image'},
    ),
    'bio': forms.Textarea(
        attrs={'class': 'form-control', 'rows': 4, 'placeholder': _('Tell others about yourself…')},
    ),
    'phone': forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '+994501234567'},
    ),
}


class TeacherProfileEditForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = (
            'profile_image',
            'bio',
            'phone',
        )
        widgets = _PROFILE_WIDGETS


class ParentProfileEditForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ('phone',)
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class StudentProfileEditForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = (
            'profile_image',
            'bio',
            'phone',
        )
        widgets = _PROFILE_WIDGETS

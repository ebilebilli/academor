from django import forms
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from portals.models import (
    Attendance,
    Lesson,
    LessonCategory,
    Schedule,
    StudentProfile,
    StudyGroup,
    VideoRecord,
)
from portals.utils.teacher_courses import teacher_groups_queryset
from portals.utils.group_services import resolve_group_lesson_service


def teacher_lesson_category_suggestions(teacher_id):
    """Distinct category labels this teacher already used (for datalist hints)."""
    return list(
        Lesson.objects.filter(teacher_id=teacher_id, category_id__isnull=False)
        .order_by('category__name')
        .values_list('category__name', flat=True)
        .distinct()
    )


def resolve_lesson_category(service, raw_name):
    """Find or create a lesson category for the given service."""
    name = (raw_name or '').strip()
    if not name or not service:
        return None
    existing = LessonCategory.objects.filter(service=service, name__iexact=name).first()
    if existing:
        return existing
    return LessonCategory.objects.create(service=service, name=name)


def _fc(attrs=None):
    base = {'class': 'form-control'}
    if attrs:
        base.update(attrs)
    return base


class TeacherGroupForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        label=_('Students'),
        queryset=StudentProfile.objects.select_related('user').order_by('user__username', 'id'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 8}),
    )

    class Meta:
        model = StudyGroup
        fields = (
            'name',
            'start_date',
            'max_students',
            'is_active',
            'students',
        )
        widgets = {
            'name': forms.TextInput(attrs=_fc()),
            'start_date': forms.DateInput(attrs=_fc({'type': 'date'})),
            'max_students': forms.NumberInput(attrs=_fc({'min': 1})),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, teacher_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_id = teacher_id
        student_filter = Q(groups__teacher_id=teacher_id, groups__is_active=True)
        if self.instance and self.instance.pk:
            student_filter |= Q(pk__in=self.instance.students.values_list('pk', flat=True))
        self.fields['students'].queryset = (
            StudentProfile.objects.filter(student_filter)
            .distinct()
            .select_related('user')
            .order_by('user__username', 'id')
        )


class TeacherScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ('group', 'weekday', 'start_time', 'duration_min', 'room_or_link', 'effective_from')
        widgets = {
            'group': forms.Select(attrs=_fc()),
            'weekday': forms.Select(attrs=_fc()),
            'start_time': forms.TimeInput(attrs=_fc({'type': 'time'})),
            'duration_min': forms.NumberInput(attrs=_fc({'min': 15, 'step': 5})),
            'room_or_link': forms.TextInput(attrs=_fc()),
            'effective_from': forms.DateInput(attrs=_fc({'type': 'date'})),
        }

    def __init__(self, teacher_id, *args, group_fixed=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_id = teacher_id
        groups = teacher_groups_queryset(teacher_id, active_only=True).order_by('name')
        if group_fixed:
            self.fields.pop('group', None)
        else:
            self.fields['group'].queryset = groups
            self.fields['group'].label = _('Group')
        if not self.initial.get('duration_min') and not self.data:
            self.initial.setdefault('duration_min', 90)
        if not self.initial.get('effective_from') and not self.data and not (self.instance and self.instance.pk):
            self.initial.setdefault('effective_from', timezone.localdate())

    def clean_group(self):
        group = self.cleaned_data.get('group')
        if group and not teacher_groups_queryset(self.teacher_id, active_only=True).filter(pk=group.pk).exists():
            raise forms.ValidationError(_('You can only schedule slots for your own groups.'))
        return group


class TeacherLessonForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        label=_('Groups'),
        queryset=StudyGroup.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'portal-lesson-group-input'}),
        help_text=_('Choose every group that should receive this lesson.'),
    )
    category_name = forms.CharField(
        label=_('Category label'),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs=_fc({
            'list': 'lesson-category-suggestions',
            'autocomplete': 'off',
            'placeholder': _('e.g. Grammar, Homework'),
        })),
        help_text=_(
            'Optional label for filtering your lessons (e.g. Grammar, Homework). '
            'Course is set automatically from the group you select.'
        ),
    )

    class Meta:
        model = Lesson
        fields = (
            'group',
            'name',
            'lesson_date',
            'description',
            'pdf_file',
            'video_url',
            'image',
        )
        widgets = {
            'group': forms.Select(attrs=_fc()),
            'name': forms.TextInput(attrs=_fc()),
            'lesson_date': forms.DateInput(attrs=_fc({'type': 'date'})),
            'description': forms.Textarea(attrs=_fc({'rows': 3})),
            'pdf_file': forms.ClearableFileInput(attrs={'class': 'portal-lesson-file-input-native', 'accept': 'application/pdf,.pdf'}),
            'video_url': forms.URLInput(attrs=_fc({'placeholder': 'https://...'})),
            'image': forms.ClearableFileInput(attrs={'class': 'portal-lesson-file-input-native', 'accept': 'image/*'}),
        }

    def __init__(self, teacher_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_id = teacher_id
        self.category_suggestions = teacher_lesson_category_suggestions(teacher_id)
        groups = teacher_groups_queryset(teacher_id, active_only=True).order_by('name')
        is_edit = bool(self.instance and self.instance.pk)
        if is_edit:
            del self.fields['groups']
            self.fields['group'].queryset = groups
            if self.instance.category_id:
                self.initial.setdefault('category_name', self.instance.category.name)
        else:
            del self.fields['group']
            self.fields['groups'].queryset = groups
            self.fields['groups'].required = True
        self.fields['name'].label = _('Name')
        self.fields['name'].required = True
        self.fields['lesson_date'].required = True
        if not self.initial.get('lesson_date') and not self.data:
            self.initial.setdefault('lesson_date', timezone.localdate())

    def _owned_groups(self):
        return teacher_groups_queryset(self.teacher_id, active_only=True)

    def _build_group_payloads(self, groups, category_name):
        owned_ids = set(self._owned_groups().values_list('pk', flat=True))
        payloads = []
        for group in groups:
            if group.pk not in owned_ids:
                return None
            service = resolve_group_lesson_service(group)
            category = resolve_lesson_category(service, category_name) if category_name else None
            payloads.append({
                'group': group,
                'subject': service,
                'category': category,
            })
        return payloads

    def clean(self):
        cleaned = super().clean()
        is_edit = bool(self.instance and self.instance.pk)
        name = (cleaned.get('name') or '').strip()
        if not name:
            self.add_error('name', _('Enter the lesson name.'))
        else:
            cleaned['name'] = name

        if is_edit:
            group = cleaned.get('group')
            groups = [group] if group else []
        else:
            groups = list(cleaned.get('groups') or [])
            if not groups:
                self.add_error('groups', _('Select at least one group.'))
                return cleaned

        category_name = (cleaned.get('category_name') or '').strip()
        cleaned['category_name'] = category_name or None

        payloads = self._build_group_payloads(groups, category_name)
        if payloads is None:
            field = 'group' if is_edit else 'groups'
            self.add_error(field, _('You can only upload lessons to your own groups.'))
            return cleaned

        cleaned['group_lessons'] = payloads
        if is_edit and payloads:
            cleaned['subject'] = payloads[0]['subject']
            cleaned['category'] = payloads[0]['category']
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.subject = self.cleaned_data['subject']
        instance.category = self.cleaned_data['category']
        if commit:
            instance.save()
        return instance

    def save_for_groups(self, teacher):
        from django.core.files.base import ContentFile

        pdf = self.cleaned_data.get('pdf_file')
        image = self.cleaned_data.get('image')
        pdf_content = pdf.read() if pdf else None
        pdf_name = pdf.name if pdf else None
        image_content = image.read() if image else None
        image_name = image.name if image else None
        shared = {
            'teacher': teacher,
            'name': self.cleaned_data['name'],
            'lesson_date': self.cleaned_data['lesson_date'],
            'description': self.cleaned_data.get('description', ''),
            'video_url': self.cleaned_data.get('video_url', ''),
        }
        lessons = []
        for payload in self.cleaned_data['group_lessons']:
            lesson = Lesson(
                group=payload['group'],
                subject=payload['subject'],
                category=payload['category'],
                **shared,
            )
            if pdf_content is not None:
                lesson.pdf_file.save(pdf_name, ContentFile(pdf_content), save=False)
            if image_content is not None:
                lesson.image.save(image_name, ContentFile(image_content), save=False)
            lesson.save()
            lessons.append(lesson)
        return lessons


def build_session_attendance_form(students, existing=None):
    existing = existing or {}
    status_choices = Attendance.Status.choices
    fields = {}
    for student in students:
        fields[f'status_{student.pk}'] = forms.ChoiceField(
            label=student.full_name,
            choices=status_choices,
            initial=existing.get(student.pk, Attendance.Status.PRESENT),
            widget=forms.RadioSelect(attrs={'class': 'portal-status-radio'}),
            required=True,
        )
    return type('SessionAttendanceForm', (forms.Form,), fields)


class TeacherVideoForm(forms.ModelForm):
    class Meta:
        model = VideoRecord
        fields = ('group', 'title', 'youtube_url', 'lesson_date', 'description')
        widgets = {
            'group': forms.Select(attrs=_fc()),
            'title': forms.TextInput(attrs=_fc()),
            'youtube_url': forms.URLInput(attrs=_fc()),
            'lesson_date': forms.DateInput(attrs=_fc({'type': 'date'})),
            'description': forms.Textarea(attrs=_fc({'rows': 3})),
        }

    def __init__(self, teacher_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = teacher_groups_queryset(
            teacher_id,
            active_only=True,
        ).order_by('name')

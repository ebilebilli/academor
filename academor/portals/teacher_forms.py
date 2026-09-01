from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from portals.models import (
    Attendance,
    Classroom,
    Lesson,
    LessonAttachment,
    LessonCategory,
    StudentProfile,
    StudyGroup,
)
from portals.utils.teacher_courses import teacher_groups_queryset
from portals.utils.group_services import resolve_group_lesson_service
from portals.utils.lesson_media import build_lesson_edit_materials, _file_basename


def _form_data_getlist(data, key, *, default=None):
    if not data:
        return default if default is not None else []
    if hasattr(data, 'getlist'):
        return data.getlist(key)
    value = data.get(key, default if default is not None else [])
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        return []


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


class TeacherGroupNameForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs=_fc()),
        }

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        if not name:
            raise forms.ValidationError(_('Enter a group name.'))
        return name



class TeacherLessonForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        label=_('Groups'),
        queryset=StudyGroup.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'portal-lesson-group-input'}),
        help_text=_(
            'Choose every group that should receive this lesson. '
            'The service (SAT, IELTS, etc.) is taken from each group\'s linked course in admin—not from your teacher profile.'
        ),
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
    pdf_files = MultipleFileField(
        label=_('PDF files'),
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'portal-lesson-file-input-native',
            'accept': 'application/pdf,.pdf',
        }),
    )
    image_files = MultipleFileField(
        label=_('Images'),
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'portal-lesson-file-input-native',
            'accept': 'image/*',
        }),
    )
    remove_attachments = forms.MultipleChoiceField(
        label=_('Remove files'),
        required=False,
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'portal-lesson-remove-input'}),
    )

    class Meta:
        model = Lesson
        fields = (
            'group',
            'name',
            'lesson_date',
            'description',
        )
        widgets = {
            'group': forms.Select(attrs=_fc()),
            'name': forms.TextInput(attrs=_fc()),
            'lesson_date': forms.DateInput(
                attrs=_fc({'type': 'date'}),
                format='%Y-%m-%d',
            ),
            'description': forms.Textarea(attrs=_fc({'rows': 3})),
        }

    def __init__(self, teacher_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_id = teacher_id
        self.category_suggestions = teacher_lesson_category_suggestions(teacher_id)
        from portals.utils.group_services import study_group_portal_display_labels

        groups = (
            teacher_groups_queryset(teacher_id, active_only=True)
            .prefetch_related('courses')
            .order_by('name')
        )
        is_edit = bool(self.instance and self.instance.pk)
        if is_edit:
            del self.fields['groups']
            self.fields['group'].queryset = groups
            if self.instance.group_id:
                labels = study_group_portal_display_labels(self.instance.group)
                self.group_service_label = ', '.join(labels) if labels else ''
            else:
                self.group_service_label = ''
            if self.instance.category_id:
                self.initial.setdefault('category_name', self.instance.category.name)
            if self.instance.lesson_date is not None and not self.data:
                self.initial['lesson_date'] = self.instance.lesson_date
            elif self.instance.lesson_date is None and not self.data:
                self.initial.setdefault('lesson_date', timezone.localdate())
            self.existing_materials = build_lesson_edit_materials(self.instance)
            selected_removals = (
                set(_form_data_getlist(self.data, 'remove_attachments'))
                if self.data
                else set()
            )
            for row in self.existing_materials:
                row['marked_for_removal'] = row['id'] in selected_removals
            self.existing_pdfs = [
                row for row in self.existing_materials
                if row['kind'] == LessonAttachment.Kind.PDF
            ]
            self.existing_images = [
                row for row in self.existing_materials
                if row['kind'] == LessonAttachment.Kind.IMAGE
            ]
            self.existing_videos = [
                row for row in self.existing_materials
                if row['kind'] == LessonAttachment.Kind.VIDEO
            ]
            self.fields['remove_attachments'].choices = [
                (row['id'], row['label']) for row in self.existing_materials
            ]
        else:
            del self.fields['group']
            del self.fields['remove_attachments']
            self.fields['groups'].queryset = groups
            self.fields['groups'].required = True
            self.fields['groups'].label_from_instance = self._lesson_group_choice_label
            self.group_service_label = ''
            self.existing_materials = []
            self.existing_pdfs = []
            self.existing_images = []
            self.existing_videos = []
        self.fields['name'].label = _('Name')
        self.fields['name'].required = True
        self.fields['lesson_date'].required = True
        self.fields['lesson_date'].input_formats = ['%Y-%m-%d']
        if not is_edit and not self.data and not self.initial.get('lesson_date'):
            self.initial.setdefault('lesson_date', timezone.localdate())

        self.new_video_url_rows = self._build_new_video_url_rows()

    @staticmethod
    def _lesson_group_choice_label(group):
        from django.utils.translation import gettext as _

        from portals.utils.group_services import study_group_portal_display_labels

        labels = study_group_portal_display_labels(group)
        service = ', '.join(labels) if labels else str(_('No course linked'))
        return f'{group.name} · {service}'

    @staticmethod
    def _empty_video_url_row():
        return {'url': ''}

    def _build_new_video_url_rows(self):
        if self.data:
            posted = _form_data_getlist(self.data, 'new_video_urls', default=[''])
            if not posted:
                posted = ['']
            return [{'url': (raw or '').strip()} for raw in posted]
        return [self._empty_video_url_row()]

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

        pdf_files = list(self.files.getlist('pdf_files')) if hasattr(self, 'files') else []
        image_files = list(self.files.getlist('image_files')) if hasattr(self, 'files') else []
        cleaned['pdf_files'] = pdf_files
        cleaned['image_files'] = image_files

        video_urls = []
        if self.data:
            validator = URLValidator()
            existing_urls = {
                row['url']
                for row in getattr(self, 'existing_materials', [])
                if row['id'] not in set(_form_data_getlist(self.data, 'remove_attachments'))
            }
            for index, raw in enumerate(_form_data_getlist(self.data, 'new_video_urls'), start=1):
                url = (raw or '').strip()
                if not url:
                    continue
                try:
                    validator(url)
                except ValidationError:
                    self.add_error(
                        'pdf_files',
                        _('New video link %(index)s is not a valid URL.') % {'index': index},
                    )
                    continue
                if url in existing_urls or url in video_urls:
                    continue
                video_urls.append(url)
        cleaned['video_urls'] = video_urls

        remove_ids = set(cleaned.get('remove_attachments') or [])
        valid_remove_ids = {row['id'] for row in getattr(self, 'existing_materials', [])}
        cleaned['remove_attachments'] = [
            item for item in remove_ids if item in valid_remove_ids
        ]
        remove_ids = set(cleaned['remove_attachments'])

        remaining_existing = sum(
            1
            for row in getattr(self, 'existing_materials', [])
            if row['id'] not in remove_ids
        )

        if not pdf_files and not image_files and not video_urls and remaining_existing == 0:
            self.add_error(
                'pdf_files',
                _('Add at least one PDF, image, or video link.'),
            )
        return cleaned

    @staticmethod
    def _read_uploads(uploaded_list):
        return [(uploaded.name, uploaded.read()) for uploaded in uploaded_list]

    @staticmethod
    def _attach_file_contents(lesson, pdf_contents, image_contents):
        from django.core.files.base import ContentFile

        for name, raw_bytes in pdf_contents:
            attachment = LessonAttachment(lesson=lesson, kind=LessonAttachment.Kind.PDF)
            attachment.file.save(name, ContentFile(raw_bytes), save=True)
        for name, raw_bytes in image_contents:
            attachment = LessonAttachment(lesson=lesson, kind=LessonAttachment.Kind.IMAGE)
            attachment.file.save(name, ContentFile(raw_bytes), save=True)

    @staticmethod
    def _reconcile_lesson_files(lesson):
        """Remove orphan legacy copies when the same filename already lives in attachments."""
        update_fields = []
        for kind, legacy_field in (
            (LessonAttachment.Kind.PDF, 'pdf_file'),
            (LessonAttachment.Kind.IMAGE, 'image'),
        ):
            legacy = getattr(lesson, legacy_field)
            if not legacy:
                continue
            legacy_name = _file_basename(legacy)
            attachment_names = [
                _file_basename(row.file)
                for row in lesson.attachments.filter(kind=kind)
                if row.file
            ]
            if legacy_name not in attachment_names:
                continue
            legacy.delete(save=False)
            setattr(lesson, legacy_field, '')
            update_fields.append(legacy_field)
        if update_fields:
            lesson.save(update_fields=update_fields)

    def _apply_removals(self, lesson):
        remove_ids = set(self.cleaned_data.get('remove_attachments') or [])
        if not remove_ids:
            return

        update_legacy = False
        for material in getattr(self, 'existing_materials', []):
            if material['id'] not in remove_ids:
                continue

            material_id = material['id']
            if material_id == 'legacy-pdf':
                if lesson.pdf_file:
                    lesson.pdf_file.delete(save=False)
                    lesson.pdf_file = ''
                    update_legacy = True
                continue

            if material_id == 'legacy-image':
                if lesson.image:
                    lesson.image.delete(save=False)
                    lesson.image = ''
                    update_legacy = True
                continue

            if material_id == 'legacy-video':
                lesson.video_url = ''
                update_legacy = True
                continue

            if not material_id.startswith('attachment-'):
                continue

            attachment = lesson.attachments.filter(pk=material['attachment_pk']).first()
            if not attachment:
                continue

            if attachment.kind == LessonAttachment.Kind.VIDEO:
                attachment.delete()
                continue

            attachment_path = attachment.file.name if attachment.file else ''
            attachment.file.delete(save=False)
            attachment.delete()

            if lesson.pdf_file and lesson.pdf_file.name == attachment_path:
                lesson.pdf_file.delete(save=False)
                lesson.pdf_file = ''
                update_legacy = True
            if lesson.image and lesson.image.name == attachment_path:
                lesson.image.delete(save=False)
                lesson.image = ''
                update_legacy = True

        if update_legacy:
            lesson.save(update_fields=['pdf_file', 'image', 'video_url'])

    @staticmethod
    def _attach_video_urls(lesson, urls):
        for url in urls:
            LessonAttachment.objects.create(
                lesson=lesson,
                kind=LessonAttachment.Kind.VIDEO,
                video_url=url,
            )

    @staticmethod
    def _sync_lesson_video_url(lesson):
        urls = []
        seen = set()
        legacy = (lesson.video_url or '').strip()
        if legacy:
            urls.append(legacy)
            seen.add(legacy)
        for attachment in lesson.attachments.filter(
            kind=LessonAttachment.Kind.VIDEO,
        ).order_by('id'):
            url = (attachment.video_url or '').strip()
            if url and url not in seen:
                urls.append(url)
                seen.add(url)
        lesson.video_url = urls[0] if urls else ''
        lesson.save(update_fields=['video_url'])

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.subject = self.cleaned_data['subject']
        instance.category = self.cleaned_data['category']
        if commit:
            instance.save()
            self._apply_removals(instance)
            pdf_contents = self._read_uploads(self.cleaned_data.get('pdf_files') or [])
            image_contents = self._read_uploads(self.cleaned_data.get('image_files') or [])
            if pdf_contents or image_contents:
                self._attach_file_contents(instance, pdf_contents, image_contents)
            video_urls = self.cleaned_data.get('video_urls') or []
            if video_urls:
                self._attach_video_urls(instance, video_urls)
            self._sync_lesson_video_url(instance)
            self._reconcile_lesson_files(instance)
        return instance

    def save_for_groups(self, teacher):
        pdf_contents = self._read_uploads(self.cleaned_data.get('pdf_files') or [])
        image_contents = self._read_uploads(self.cleaned_data.get('image_files') or [])
        shared = {
            'teacher': teacher,
            'name': self.cleaned_data['name'],
            'lesson_date': self.cleaned_data['lesson_date'],
            'description': self.cleaned_data.get('description', ''),
            'video_url': '',
        }
        lessons = []
        video_urls = self.cleaned_data.get('video_urls') or []
        for payload in self.cleaned_data['group_lessons']:
            lesson = Lesson(
                group=payload['group'],
                subject=payload['subject'],
                category=payload['category'],
                **shared,
            )
            lesson.save()
            if pdf_contents or image_contents:
                self._attach_file_contents(lesson, pdf_contents, image_contents)
            if video_urls:
                self._attach_video_urls(lesson, video_urls)
                self._sync_lesson_video_url(lesson)
            lessons.append(lesson)
        return lessons


class TeacherTextbookForm(forms.ModelForm):
    remove_pdf = forms.BooleanField(
        label=_('Remove PDF'),
        required=False,
    )

    class Meta:
        model = Classroom
        fields = ('group', 'name', 'description', 'pdf_file')
        widgets = {
            'group': forms.Select(attrs=_fc()),
            'name': forms.TextInput(attrs=_fc()),
            'description': forms.Textarea(attrs=_fc({'rows': 3})),
            'pdf_file': forms.ClearableFileInput(attrs={
                'class': 'portal-lesson-file-input-native',
                'accept': 'application/pdf,.pdf',
            }),
        }

    def __init__(self, teacher_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_id = teacher_id
        self.fields['group'].queryset = teacher_groups_queryset(
            teacher_id,
            active_only=True,
        ).order_by('name')
        self.fields['group'].label = _('Group')
        self.fields['name'].label = _('Name')
        self.fields['name'].required = True
        self.fields['pdf_file'].required = not (self.instance and self.instance.pk)
        if self.instance and self.instance.pk and self.instance.pdf_file:
            self.existing_pdf = {
                'label': _file_basename(self.instance.pdf_file),
                'url': self.instance.pdf_file.url,
                'marked_for_removal': bool(self.data.get('remove_pdf')),
            }
        else:
            self.existing_pdf = None

    def clean(self):
        cleaned = super().clean()
        is_edit = bool(self.instance and self.instance.pk)
        remove_pdf = bool(cleaned.get('remove_pdf'))
        pdf_file = cleaned.get('pdf_file')
        has_existing = bool(is_edit and self.instance.pdf_file and not remove_pdf)
        if not pdf_file and not has_existing:
            self.add_error('pdf_file', _('Upload a PDF file.'))
        return cleaned

    def clean_group(self):
        group = self.cleaned_data.get('group')
        if group and not teacher_groups_queryset(self.teacher_id, active_only=True).filter(pk=group.pk).exists():
            raise forms.ValidationError(_('You can only add textbooks for your own groups.'))
        return group

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        if not name:
            raise forms.ValidationError(_('Enter the textbook name.'))
        return name

    def save(self, commit=True, teacher=None):
        instance = super().save(commit=False)
        if teacher is not None:
            instance.teacher = teacher
        remove_pdf = self.cleaned_data.get('remove_pdf')
        new_pdf = self.cleaned_data.get('pdf_file')
        if remove_pdf and not new_pdf and instance.pdf_file:
            instance.pdf_file.delete(save=False)
            instance.pdf_file = ''
        if commit:
            instance.save()
            self.save_m2m()
        return instance


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


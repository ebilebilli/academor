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
        from portals.utils.teacher_students import teacher_students_q

        student_filter = teacher_students_q(teacher_id) & Q(is_active=True)
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
            'You can also send it straight to chosen students below.'
        ),
    )
    students = forms.ModelMultipleChoiceField(
        label=_('Students'),
        queryset=StudentProfile.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'portal-lesson-student-input'}),
        help_text=_('Send the lesson straight to these students (with or without a group).'),
    )
    quizzes = forms.ModelMultipleChoiceField(
        label=_('Homework quizzes'),
        queryset=Lesson.quizzes.rel.model.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'portal-lesson-quiz-input'}),
        help_text=_(
            'Quizzes attached here open automatically for everyone who receives the lesson; '
            'you see each student\'s result on the lesson page.'
        ),
    )
    service = forms.ChoiceField(
        label=_('Service'),
        required=False,
        choices=(),
        widget=forms.Select(attrs={'class': 'form-select'}),
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
        help_text=_('Optional label for filtering your lessons (e.g. Grammar, Homework).'),
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
        from portals.utils.group_services import teacher_lesson_service_choices
        from portals.utils.teacher_students import teacher_students_qs

        groups = (
            teacher_groups_queryset(teacher_id, active_only=True)
            .order_by('name')
        )
        is_edit = bool(self.instance and self.instance.pk)

        # recipients besides groups: the teacher's own students (a student may have no group)
        students_qs = teacher_students_qs(teacher_id)
        if is_edit:
            students_qs = (
                StudentProfile.objects.filter(
                    Q(pk__in=students_qs.values('pk'))
                    | Q(pk__in=self.instance.students.values('pk'))
                )
            )
        self.fields['students'].queryset = (
            students_qs.select_related('user').order_by('user__username', 'id')
        )
        self.fields['students'].label_from_instance = lambda student: student.full_name

        # homework quizzes: the quizzes of the teacher's own services
        self.fields['quizzes'].queryset = self._teacher_quiz_queryset(teacher_id, is_edit)
        self.fields['quizzes'].label_from_instance = self._quiz_choice_label

        service_choices = teacher_lesson_service_choices(teacher_id)
        self.fields['service'].choices = service_choices
        self.show_service_field = len(service_choices) > 1
        self.group_service_label = ''
        if is_edit:
            del self.fields['groups']
            self.fields['group'].queryset = groups
            self.fields['group'].required = False
            self.fields['group'].empty_label = _('No group — chosen students only')
            if not self.data:
                self.initial.setdefault(
                    'students',
                    list(self.instance.students.values_list('pk', flat=True)),
                )
                self.initial.setdefault(
                    'quizzes',
                    list(self.instance.quizzes.values_list('pk', flat=True)),
                )
                self.initial.setdefault('service', self.instance.subject)
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
            self.fields['groups'].required = False
            self.fields['groups'].label_from_instance = self._lesson_group_choice_label
            if service_choices and not self.data:
                self.initial.setdefault('service', service_choices[0][0])
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
        return group.name

    @staticmethod
    def _quiz_choice_label(quiz):
        # shown under its category heading (see quiz_option_groups)
        return quiz.topic

    def quiz_option_groups(self):
        """Homework quiz options under their category headings, for the pick list."""
        if 'quizzes' not in self.fields:
            return []
        categories = {
            quiz.pk: (quiz.category.name if quiz.category_id else '')
            for quiz in self.fields['quizzes'].queryset
        }
        groups = []
        index = {}
        for option in self['quizzes']:
            raw = option.data['value']
            pk = getattr(raw, 'value', raw)
            label = categories.get(pk, '')
            if label not in index:
                index[label] = {'label': label or str(_('Other')), 'options': []}
                groups.append(index[label])
            index[label]['options'].append(option)
        return groups

    def _teacher_quiz_queryset(self, teacher_id, is_edit):
        """Quizzes of the teacher's services (plus the ones already attached on edit)."""
        from portals.models import Quiz
        from portals.utils.quiz_category_services import quiz_category_slugs_for_portal_codes
        from portals.utils.student_courses import quiz_visible_to_teacher
        from portals.utils.teacher_courses import get_teacher_course_type_codes

        slugs = quiz_category_slugs_for_portal_codes(get_teacher_course_type_codes(teacher_id))
        candidates = (
            Quiz.objects.filter(category__services__slug__in=slugs)
            .select_related('category')
            .prefetch_related('category__services')
            .distinct()
        ) if slugs else Quiz.objects.none()
        visible_ids = {quiz.pk for quiz in candidates if quiz_visible_to_teacher(quiz, teacher_id)}
        if is_edit:
            visible_ids |= set(self.instance.quizzes.values_list('pk', flat=True))
        return (
            Quiz.objects.filter(pk__in=visible_ids)
            .select_related('category')
            .order_by('category__name', 'topic', 'id')
        )

    def _lesson_service(self, cleaned):
        """Service the lesson is filed under: the chosen one, else the teacher's first."""
        from portals.utils.group_services import resolve_teacher_default_lesson_service

        chosen = (cleaned.get('service') or '').strip()
        if chosen:
            return chosen
        if self.instance and self.instance.pk and self.instance.subject:
            return self.instance.subject
        return resolve_teacher_default_lesson_service(self.teacher_id)

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

    def _build_group_payloads(self, groups, category_name, service):
        owned_ids = set(self._owned_groups().values_list('pk', flat=True))
        payloads = []
        for group in groups:
            if group.pk not in owned_ids:
                return None
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

        students = list(cleaned.get('students') or [])
        if is_edit:
            group = cleaned.get('group')
            groups = [group] if group else []
        else:
            groups = list(cleaned.get('groups') or [])
        # a lesson goes to a group or straight to students: one of them is needed
        if not groups and not students:
            self.add_error(
                'group' if is_edit else 'groups',
                _('Select at least one group or one student.'),
            )
            return cleaned

        category_name = (cleaned.get('category_name') or '').strip()
        cleaned['category_name'] = category_name or None
        service = self._lesson_service(cleaned)

        payloads = self._build_group_payloads(groups, category_name, service)
        if payloads is None:
            field = 'group' if is_edit else 'groups'
            self.add_error(field, _('You can only upload lessons to your own groups.'))
            return cleaned

        cleaned['group_lessons'] = payloads
        cleaned['subject'] = service
        cleaned['category'] = (
            resolve_lesson_category(service, category_name) if category_name else None
        )

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
            # to a group, or straight to the chosen students (never both on one lesson)
            instance.students.set(
                [] if instance.group_id else (self.cleaned_data.get('students') or [])
            )
            instance.quizzes.set(self.cleaned_data.get('quizzes') or [])
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
        quizzes = list(self.cleaned_data.get('quizzes') or [])
        direct_students = list(self.cleaned_data.get('students') or [])
        targets = [
            {'group': payload['group'], 'category': payload['category'], 'students': []}
            for payload in self.cleaned_data['group_lessons']
        ]
        if direct_students:
            # one more lesson with no group: it goes straight to the chosen students
            targets.append({
                'group': None,
                'category': self.cleaned_data.get('category'),
                'students': direct_students,
            })
        for target in targets:
            lesson = Lesson(
                group=target['group'],
                subject=self.cleaned_data['subject'],
                category=target['category'],
                **shared,
            )
            lesson.save()
            if target['students']:
                lesson.students.set(target['students'])
            if quizzes:
                lesson.quizzes.set(quizzes)
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



# ---------------------------------------------------------------- students made by a teacher
def student_service_choices(lang=None):
    """Teaching services a student can be enrolled in: (portal code, label), one per code."""
    from portals.utils.portal_services import (
        get_active_services_queryset,
        infer_course_type_for_service,
        resolve_course_type_label,
    )

    choices = []
    seen = set()
    for service in get_active_services_queryset():
        if getattr(service, 'is_mock_test', False):
            continue  # mock-test SKUs are sold to customers, they are not a study service
        code = infer_course_type_for_service(service) or (service.slug or '').strip()
        if not code or code in seen:
            continue
        seen.add(code)
        choices.append((code, resolve_course_type_label(code, lang) or code))
    return choices


class TeacherStudentCreateForm(forms.Form):
    """A teacher adds a student: a real portal student, in the system straight away."""

    full_name = forms.CharField(
        label=_('Ad və soyad'),
        max_length=150,
        widget=forms.TextInput(attrs=_fc({'autocomplete': 'off'})),
        help_text=_('Tələbə portala bu adla daxil olur.'),
    )
    phone = forms.CharField(
        label=_('Telefon'),
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs=_fc({'autocomplete': 'off', 'inputmode': 'tel'})),
    )
    services = forms.MultipleChoiceField(
        label=_('Xidmətlər'),
        choices=(),
        widget=forms.CheckboxSelectMultiple(),
        help_text=_(
            'Tələbənin quizləri, mock testləri və bildirişləri bu xidmətlərə görə açılır. '
            'IELTS tələbələrində General English əvvəlcədən aktivdir.'
        ),
    )
    group = forms.ModelChoiceField(
        label=_('Qrup'),
        queryset=StudyGroup.objects.none(),
        required=False,
        empty_label=_('Qrupsuz'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text=_('Qrup yalnız siyahıda filtrləmək üçündür; tələbə qrupsuz da ola bilər.'),
    )
    password = forms.CharField(
        label=_('Parol'),
        required=False,
        min_length=6,
        max_length=128,
        widget=forms.TextInput(attrs=_fc({'autocomplete': 'off'})),
        help_text=_('Boş qalsa tələbə portala daxil ola bilməz; parolu sonra admin təyin edə bilər.'),
    )

    def __init__(self, teacher_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from portals.utils.quiz_assignments import _canonical_course_code
        from portals.utils.student_courses import GENERAL_ENGLISH_COURSE_CODE, IELTS_COURSE_CODE
        from portals.utils.teacher_courses import get_teacher_course_type_codes

        self.teacher_id = teacher_id
        choices = student_service_choices()
        self.fields['services'].choices = choices
        self.fields['group'].queryset = (
            teacher_groups_queryset(teacher_id, active_only=True).order_by('name', 'id')
        )
        if not self.is_bound:
            valid = {code for code, _label in choices}
            initial = {
                _canonical_course_code(code)
                for code in get_teacher_course_type_codes(teacher_id)
            } & valid
            if IELTS_COURSE_CODE in initial and GENERAL_ENGLISH_COURSE_CODE in valid:
                initial.add(GENERAL_ENGLISH_COURSE_CODE)
            self.initial.setdefault('services', sorted(initial))

    def clean_full_name(self):
        from django.contrib.auth import get_user_model

        from portals.utils.username_validators import portal_username_validator

        name = ' '.join((self.cleaned_data.get('full_name') or '').split())
        if not name:
            raise ValidationError(_('Ad və soyadı yazın.'))
        portal_username_validator(name)
        if get_user_model().objects.filter(username__iexact=name).exists():
            raise ValidationError(_('Bu adla istifadəçi artıq var. Ada fərqləndirici əlavə edin.'))
        return name

    def clean_phone(self):
        from portals.utils.normalize_phone_number import phone_number_validator

        phone = (self.cleaned_data.get('phone') or '').strip()
        if phone:
            phone_number_validator(phone)
        return phone

    def clean_group(self):
        group = self.cleaned_data.get('group')
        if group and group.max_students and group.students.count() >= group.max_students:
            raise ValidationError(
                _('Bu qrupda yer yoxdur (ən çox %(limit)s tələbə).') % {'limit': group.max_students},
            )
        return group

    def save(self):
        """Create the user, the student profile, the teacher link, the group and the services."""
        from portals.utils.teacher_students import create_teacher_student

        data = self.cleaned_data
        return create_teacher_student(
            self.teacher_id,
            data['full_name'],
            services=list(data.get('services') or []),
            group=data.get('group'),
            phone=data.get('phone') or '',
            password=data.get('password') or '',
        )


class TeacherGroupCreateForm(forms.Form):
    name = forms.CharField(
        label=_('Qrupun adı'),
        max_length=200,
        widget=forms.TextInput(attrs=_fc({'autocomplete': 'off'})),
    )

    def __init__(self, teacher_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_id = teacher_id

    def clean_name(self):
        name = ' '.join((self.cleaned_data.get('name') or '').split())
        if not name:
            raise ValidationError(_('Enter a group name.'))
        if StudyGroup.objects.filter(
            teacher_id=self.teacher_id,
            is_active=True,
            name__iexact=name,
        ).exists():
            raise ValidationError(_('Bu adda qrupunuz artıq var.'))
        return name

    def save(self):
        """A real group straight away: only a name, used for filtering."""
        return StudyGroup.objects.create(
            teacher_id=self.teacher_id,
            name=self.cleaned_data['name'],
            is_active=True,
            is_register_only=False,
            max_students=50,
        )

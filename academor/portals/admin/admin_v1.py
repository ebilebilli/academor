from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count, Q
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from portals.admin.filters import (
    DateJoinedMonthFilter,
    DateJoinedPeriodFilter,
    DateJoinedYearFilter,
    PortalRoleFilter,
)
from portals.admin.display import (
    portal_admin_change_link,
    portal_capacity_bar,
    portal_count_badge,
    portal_course_pill,
    portal_day_badge,
    portal_person_cell,
    portal_role_badge,
    portal_score_chip,
)
from portals.admin.mixins import CourseTypeTabFilterMixin, PortalModelAdmin
from portals.admin.reading_inline_formsets import (
    ReadingQuestionGroupInlineFormSet,
    ReadingQuestionInlineFormSet,
    link_pending_reading_question_groups,
)
from portals.admin.quiz_forms import (
    ListeningQuestionAdminForm,
    QuizQuestionAdminForm,
    ReadingQuestionAdminForm,
    ReadingQuestionGroupAdminForm,
    SpeakingPartAdminForm,
)
from portals.forms import (
    PORTAL_ROLE_CHOICES,
    PortalUserChangeForm,
    PortalUserCreationForm,
    get_user_portal_role,
)
from portals.utils.admin_access import can_access_django_admin, strip_admin_flags_for_portal_user
from portals.utils.group_services import (
    students_matching_group_courses,
    study_group_portal_codes,
)
from portals.utils.portal_services import (
    expand_course_types_to_service_slugs,
    get_active_course_type_choices,
    get_active_services_queryset,
    get_course_type_label_map,
    portal_codes_for_service_ids,
    resolve_course_type_label,
)
from portals.utils.teacher_courses import (
    teacher_has_all_course_codes,
    teachers_for_portal_course_codes,
)
from portals.models.score_models import WEEKLY_SCORE_MAX
from portals.models import (
    QuizResultReview,
    PortalNotification,
    IeltsMockTestAttempt,
    SpeakingRecording,
    LessonAttachment,
    Attendance,
    Classroom,
    Lesson,
    LessonCategory,
    LessonHomework,
    ListeningAudio,
    ListeningQuestion,
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionGroup,
    ParentProfile,
    CustomerProfile,
    Quiz,
    QuizAssignment,
    QuizCategory,
    QuizQuestion,
    QuizResult,
    Schedule,
    Score,
    WeeklyStudentScore,
    SpeakingPart,
    SpeakingQuestion,
    StudentProfile,
    StudentCourseSpecialization,
    StudyGroup,
    TeacherProfile,
    TeacherCourseSpecialization,
    VideoRecord,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# User (login accounts) — role + profile on create
# ---------------------------------------------------------------------------

if admin.site.is_registered(User):
    admin.site.unregister(User)


@admin.register(User)
class PortalUserAdmin(BaseUserAdmin):
    add_form = PortalUserCreationForm
    form = PortalUserChangeForm
    list_display = (
        'username',
        'portal_role_display',
        'portal_username_display',
        'portal_phone_display',
        'is_staff',
        'is_active',
    )
    list_filter = (
        PortalRoleFilter,
        DateJoinedPeriodFilter,
        DateJoinedYearFilter,
        DateJoinedMonthFilter,
        'is_staff',
        'is_superuser',
        'is_active',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    class Media:
        js = ('portals/admin/js/user_password_generator.js',)
        css = {'all': ('portals/css/portal-admin.css',)}

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Role & profile', {
            'classes': ('wide', 'portal-fieldset'),
            'description': _(
                'Pick a role and optional phone. Teacher, Student, Parent, and Customer '
                'accounts get a portal profile automatically. Staff can use Django admin. '
                'Admin has full superuser access. Display name is the username.'
            ),
            'fields': ('portal_role', 'phone', 'teacher_courses', 'linked_students', 'mock_credits', 'assigned_teacher'),
        }),
    )

    readonly_fields = (
        'portal_role_display',
        'portal_username_display',
        'portal_phone_display',
        'portal_mock_credits_display',
        'portal_profile_link',
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        fieldsets = list(super().get_fieldsets(request, obj))
        if self._get_linked_profile(obj):
            fieldsets = [
                fs for fs in fieldsets
                if fs[0] not in ('Permissions',)
            ]
        fieldsets.append((
            'Portal account',
            {
                'classes': ('portal-fieldset',),
                'fields': (
                    'portal_role_display',
                    'portal_username_display',
                    'portal_phone_display',
                    'portal_mock_credits_display',
                    'portal_profile_link',
                ),
            },
        ))
        return fieldsets

    def save_form(self, request, form, change):
        # ModelAdmin.save_form() calls form.save(commit=False), which skips
        # PortalUserCreationForm profile creation — use commit=True on add.
        if not change:
            return form.save(commit=True)
        return super().save_form(request, form, change)

    def save_model(self, request, obj, form, change):
        if self._get_linked_profile(obj):
            obj.is_staff = False
            obj.is_superuser = False
        super().save_model(request, obj, form, change)
        strip_admin_flags_for_portal_user(obj)

    def has_module_permission(self, request):
        return can_access_django_admin(request.user)

    @admin.display(description='Role')
    def portal_role_display(self, obj):
        role = get_user_portal_role(obj)
        labels = dict(PORTAL_ROLE_CHOICES)
        if not role:
            return '—'
        tone = role if role in ('teacher', 'student', 'parent', 'customer') else 'default'
        return portal_role_badge(labels.get(role, role), tone)

    @admin.display(description=_('Username'))
    def portal_username_display(self, obj):
        profile = self._get_linked_profile(obj)
        if profile:
            return profile.full_name
        return obj.get_username() or '—'

    @admin.display(description='Phone')
    def portal_phone_display(self, obj):
        profile = self._get_linked_profile(obj)
        if profile and getattr(profile, 'phone', None):
            return profile.phone
        return '—'

    @admin.display(description=_('Mock credits'))
    def portal_mock_credits_display(self, obj):
        profile = self._get_linked_profile(obj)
        if isinstance(profile, CustomerProfile):
            return _('IELTS: %(ielts)s, SAT: %(sat)s') % {
                'ielts': profile.ielts_mock_credits,
                'sat': profile.sat_mock_credits,
            }
        return '—'

    @admin.display(description=_('Portal profile'))
    def portal_profile_link(self, obj):
        profile = self._get_linked_profile(obj)
        if not profile:
            return '—'
        return portal_admin_change_link(profile, _('Open profile'))

    def _get_linked_profile(self, obj):
        if not obj or not obj.pk:
            return None
        # Memoized per row: several list columns call this, and each lookup
        # is up to three queries.
        if not hasattr(obj, '_portal_linked_profile'):
            obj._portal_linked_profile = (
                TeacherProfile.objects.filter(user_id=obj.pk).first()
                or StudentProfile.objects.filter(user_id=obj.pk).first()
                or ParentProfile.objects.filter(user_id=obj.pk).first()
                or CustomerProfile.objects.filter(user_id=obj.pk).first()
            )
        return obj._portal_linked_profile


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------

class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 0
    fields = ('weekday', 'start_time', 'duration_min', 'room_or_link', 'effective_from')
    verbose_name = 'Weekly slot'
    verbose_name_plural = 'Weekly schedule (recurring slots)'
    classes = ('portal-schedule-inline',)


class StudentCourseSpecializationForm(forms.ModelForm):
    class Meta:
        model = StudentCourseSpecialization
        fields = ('course_type', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = list(get_active_course_type_choices())
        existing = getattr(self.instance, 'course_type', None)
        if existing and existing not in {code for code, _ in choices}:
            choices = [(existing, resolve_course_type_label(existing)), *choices]
        self.fields['course_type'] = forms.ChoiceField(
            label=_('Course / service'),
            choices=choices,
            required=True,
        )


class StudentCourseSpecializationInline(admin.TabularInline):
    model = StudentCourseSpecialization
    form = StudentCourseSpecializationForm
    extra = 0
    min_num = 0
    fields = ('course_type', 'is_active')
    verbose_name = _('Service enrollment')
    verbose_name_plural = _('Service enrollments')


class TeacherCourseSpecializationForm(forms.ModelForm):
    class Meta:
        model = TeacherCourseSpecialization
        fields = ('course_type',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = list(get_active_course_type_choices())
        existing = getattr(self.instance, 'course_type', None)
        if existing and existing not in {code for code, _ in choices}:
            choices = [(existing, resolve_course_type_label(existing)), *choices]
        self.fields['course_type'] = forms.ChoiceField(
            label=_('Course / service'),
            choices=choices,
            required=True,
        )


class TeacherCourseSpecializationInline(admin.TabularInline):
    model = TeacherCourseSpecialization
    form = TeacherCourseSpecializationForm
    extra = 1
    min_num = 0
    fields = ('course_type',)
    verbose_name = _('Course specialization')
    verbose_name_plural = _('Course specializations')


class QuizQuestionInline(admin.StackedInline):
    model = QuizQuestion
    form = QuizQuestionAdminForm
    extra = 1
    fields = (
        'order',
        'prompt_type',
        'question',
        'media_file',
        'media_url',
        'answer_options',
        'correct_answer',
        'student_response_preview',
    )
    ordering = ('order', 'id')
    verbose_name = _('Question')
    verbose_name_plural = _('Questions')
    classes = ('portal-quiz-inline',)


class ListeningQuestionInline(admin.StackedInline):
    model = ListeningQuestion
    form = ListeningQuestionAdminForm
    extra = 0
    fields = ('order', 'question', 'answer_options', 'correct_answer')
    ordering = ('order', 'id')
    verbose_name = _('Listening question')
    verbose_name_plural = _('Listening questions (student answer lines)')


class ListeningAudioInline(admin.StackedInline):
    model = ListeningAudio
    extra = 0
    fields = (
        'order',
        'title',
        'description',
        'audio_file',
        'audio_url',
    )
    ordering = ('order', 'id')
    show_change_link = True
    verbose_name = _('Listening audio')
    verbose_name_plural = _('Listening audio sections (add audio, then edit questions)')


class ReadingQuestionInline(admin.StackedInline):
    model = ReadingQuestion
    form = ReadingQuestionAdminForm
    formset = ReadingQuestionInlineFormSet
    extra = 0
    fields = (
        'order',
        'group_ref',
        'question_type',
        'question',
        'answer_options',
        'correct_answer',
        'word_limit',
        'case_insensitive',
        'accept_alternatives_text',
        'question_config',
    )
    ordering = ('order', 'id')
    verbose_name = _('Reading question')
    verbose_name_plural = _('Reading questions')


class ReadingQuestionGroupInline(admin.StackedInline):
    model = ReadingQuestionGroup
    form = ReadingQuestionGroupAdminForm
    formset = ReadingQuestionGroupInlineFormSet
    extra = 0
    fields = ('order', 'title', 'instructions', 'question_type', 'option_pool')
    ordering = ('order', 'id')
    show_change_link = True
    verbose_name = _('Reading question group')
    verbose_name_plural = _('Matching question groups')


class ReadingPassageInline(admin.StackedInline):
    model = ReadingPassage
    extra = 0
    fields = ('order', 'title', 'instructions', 'body')
    ordering = ('order', 'id')
    show_change_link = True
    verbose_name = _('Reading passage')
    verbose_name_plural = _('Reading passages (add passage, then edit questions)')


class SpeakingQuestionInline(admin.StackedInline):
    model = SpeakingQuestion
    extra = 0
    fields = ('order', 'question', 'preparation_seconds', 'answer_seconds')
    ordering = ('order', 'id')
    verbose_name = _('Speaking question')
    verbose_name_plural = _('Speaking questions')


class SpeakingPartInline(admin.StackedInline):
    model = SpeakingPart
    extra = 0
    fields = (
        'order',
        'part_type',
        'title',
        'instructions',
        'cue_card_topic',
        'cue_card_bullets',
        'preparation_seconds',
        'default_answer_seconds',
    )
    ordering = ('order', 'id')
    show_change_link = True
    verbose_name = _('Speaking part')
    verbose_name_plural = _('Speaking parts (IELTS Part 1–3, then edit questions)')


@admin.register(ReadingPassage)
class ReadingPassageAdmin(PortalModelAdmin):
    list_display = (
        'title',
        'quiz_display',
        'order',
        'question_count_display',
    )
    list_display_links = ('title',)
    list_filter = ('quiz__category__services',)
    search_fields = ('title', 'body', 'quiz__topic', 'quiz__category__name')
    autocomplete_fields = ('quiz',)
    ordering = ('quiz', 'order', 'id')
    inlines = (ReadingQuestionGroupInline, ReadingQuestionInline,)
    fieldsets = (
        (None, {
            'description': _(
                'Each passage belongs to a reading quiz. '
                'Add matching groups and questions in the sections below.'
            ),
            'fields': ('quiz', 'order', 'title', 'instructions', 'body'),
        }),
    )

    class Media:
        css = {'all': ('portals/css/quiz-question-admin.css',)}
        js = ('portals/admin/js/reading-passage-admin.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'group-options/',
                self.admin_site.admin_view(self.group_options_view),
                name='portals_readingpassage_group_options',
            ),
            path(
                'question-type-fields/',
                self.admin_site.admin_view(self.question_type_fields_view),
                name='portals_readingpassage_question_type_fields',
            ),
        ]
        return custom + urls

    def group_options_view(self, request):
        passage_id = request.GET.get('passage_id')
        if not passage_id:
            return JsonResponse({'groups': []})
        try:
            passage_pk = int(passage_id)
        except (TypeError, ValueError):
            return JsonResponse({'groups': []})
        groups = (
            ReadingQuestionGroup.objects.filter(passage_id=passage_pk)
            .order_by('order', 'id')
            .values('id', 'title', 'order', 'question_type')
        )
        return JsonResponse({
            'groups': [
                {
                    'id': row['id'],
                    'title': row['title'] or '',
                    'order': row['order'],
                    'question_type': row['question_type'],
                }
                for row in groups
            ],
        })

    def question_type_fields_view(self, request):
        if request.method != 'POST':
            return JsonResponse({'error': _('POST required.')}, status=405)

        from portals.utils.quiz_reading_admin import reading_question_admin_field_config

        return JsonResponse(
            reading_question_admin_field_config(request.POST.get('question_type')),
        )

    def save_related(self, request, form, formsets, change):
        group_formset = None
        question_formset = None
        for inline_formset in formsets:
            if inline_formset.model is ReadingQuestionGroup:
                group_formset = inline_formset
            elif inline_formset.model is ReadingQuestion:
                question_formset = inline_formset

        super().save_related(request, form, formsets, change)
        link_pending_reading_question_groups(group_formset, question_formset)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context['reading_group_options_url'] = reverse(
            'admin:portals_readingpassage_group_options',
        )
        context['reading_question_type_fields_url'] = reverse(
            'admin:portals_readingpassage_question_type_fields',
        )
        return super().render_change_form(request, context, add, change, form_url, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'quiz':
            kwargs['queryset'] = Quiz.objects.filter(is_reading=True).select_related('category')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description=_('Quiz'))
    def quiz_display(self, obj):
        if not obj.quiz_id:
            return '—'
        return portal_admin_change_link(obj.quiz, obj.quiz.topic)

    @admin.display(description=_('Questions'))
    def question_count_display(self, obj):
        count = obj.questions.count()
        return portal_count_badge(count, 'questions', tone='teal')


@admin.register(ListeningAudio)
class ListeningAudioAdmin(PortalModelAdmin):
    list_display = (
        'title',
        'quiz_display',
        'order',
        'question_count_display',
    )
    list_display_links = ('title',)
    list_filter = ('quiz__category__services',)
    search_fields = ('title', 'description', 'quiz__topic', 'quiz__category__name')
    autocomplete_fields = ('quiz',)
    ordering = ('quiz', 'order', 'id')
    inlines = (ListeningQuestionInline,)
    fieldsets = (
        (None, {
            'description': _(
                'Each audio clip belongs to a listening quiz. '
                'Add listening questions in the section below.'
            ),
            'fields': ('quiz', 'order', 'title', 'description', 'audio_file', 'audio_url'),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'quiz':
            kwargs['queryset'] = Quiz.objects.filter(is_listening=True).select_related('category')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description=_('Quiz'))
    def quiz_display(self, obj):
        if not obj.quiz_id:
            return '—'
        return portal_admin_change_link(obj.quiz, obj.quiz.topic)

    @admin.display(description=_('Questions'))
    def question_count_display(self, obj):
        count = obj.questions.count()
        return portal_count_badge(count, 'questions', tone='teal')


@admin.register(SpeakingPart)
class SpeakingPartAdmin(PortalModelAdmin):
    form = SpeakingPartAdminForm
    list_display = (
        'title',
        'quiz_display',
        'part_type',
        'order',
        'question_count_display',
    )
    list_display_links = ('title',)
    list_filter = ('part_type', 'quiz__category__services')
    search_fields = ('title', 'instructions', 'cue_card_topic', 'quiz__topic', 'quiz__category__name')
    autocomplete_fields = ('quiz',)
    ordering = ('quiz', 'order', 'id')
    inlines = (SpeakingQuestionInline,)
    def get_fieldsets(self, request, obj=None):
        part_fields = (
            'order',
            'part_type',
            'title',
            'instructions',
            'cue_card_topic',
            'cue_card_bullets',
            'preparation_seconds',
            'default_answer_seconds',
        )
        if obj and obj.pk:
            return (
                (None, {
                    'description': _(
                        'Each part belongs to a speaking quiz. '
                        'Use official IELTS timing defaults or override per part. '
                        'Add speaking questions in the section below.',
                    ),
                    'fields': ('quiz', *part_fields),
                }),
            )
        return (
            (None, {
                'description': _(
                    'Each part belongs to a speaking quiz. '
                    'Select an existing speaking quiz, or leave Quiz empty and enter '
                    'a new topic and category — a speaking quiz will be created automatically. '
                    'Add speaking questions in the section below.',
                ),
                'fields': ('quiz', 'new_quiz_topic', 'new_quiz_category', *part_fields),
            }),
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'quiz':
            kwargs['queryset'] = Quiz.objects.filter(is_speaking=True).select_related('category')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description=_('Quiz'))
    def quiz_display(self, obj):
        if not obj.quiz_id:
            return '—'
        return portal_admin_change_link(obj.quiz, obj.quiz.topic)

    @admin.display(description=_('Questions'))
    def question_count_display(self, obj):
        count = obj.questions.count()
        return portal_count_badge(count, 'questions', tone='teal')


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

def _profile_photo_url(obj) -> str | None:
    try:
        if obj.profile_image:
            return obj.profile_image.url
    except (ValueError, AttributeError):
        pass
    return None


def _profile_image_preview(obj):
    url = _profile_photo_url(obj)
    if not url:
        return format_html('<span class="portal-person__sub">No photo uploaded</span>')
    return format_html(
        '<img src="{}" alt="" class="portal-profile-preview">',
        url,
    )


@admin.register(TeacherProfile)
class TeacherProfileAdmin(PortalModelAdmin):
    inlines = (TeacherCourseSpecializationInline,)
    list_display = (
        'full_name_link',
        'person_display',
        'user_link',
        'course_specializations_display',
        'group_count_display',
    )
    list_display_links = ('full_name_link',)
    list_filter = ('course_specializations__course_type',)
    search_fields = (
        'phone',
        'specialization',
        'user__username',
        'user__email',
    )
    autocomplete_fields = ('user',)
    readonly_fields = ('profile_image_preview',)
    ordering = ('user__username', 'id')
    list_per_page = 25
    fieldsets = (
        (_('Login account'), {
            'classes': ('portal-fieldset',),
            'description': _(
                'Pick an existing login account, or create one under Users with role '
                'Teacher — a profile is created automatically.'
            ),
            'fields': ('user',),
        }),
        (_('Personal information'), {
            'classes': ('portal-fieldset',),
            'fields': (
                'profile_image',
                'profile_image_preview',
                'phone',
                'bio',
            ),
        }),
        (_('Social media'), {
            'classes': ('portal-fieldset',),
            'fields': ('instagram', 'facebook', 'linkedin', 'youtube'),
        }),
    )

    def get_portal_stats(self, request):
        total = TeacherProfile.objects.count()
        with_groups = TeacherProfile.objects.filter(groups__isnull=False).distinct().count()
        return [
            {'value': total, 'label': _('Teachers'), 'tone': 'purple'},
            {'value': with_groups, 'label': _('With groups'), 'tone': 'teal'},
        ]

    def get_search_results(self, request, queryset, search_term):
        if (
            request.GET.get('app_label') == 'portals'
            and request.GET.get('model_name') == 'studygroup'
            and request.GET.get('field_name') == 'teacher'
        ):
            raw_ids = (request.GET.get('group_courses') or '').strip()
            if raw_ids:
                service_ids = [part for part in raw_ids.split(',') if part]
                codes = portal_codes_for_service_ids(service_ids)
                if codes:
                    queryset = teachers_for_portal_course_codes(codes)
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    @admin.display(description=_('Teacher'))
    def full_name_link(self, obj):
        return obj.full_name

    @admin.display(description=_('Teacher'))
    def person_display(self, obj):
        labels = obj.get_course_type_labels()
        subtitle = ', '.join(labels) if labels else _('No course assigned')
        return portal_person_cell(
            obj.full_name,
            subtitle=subtitle,
            role='teacher',
            photo_url=_profile_photo_url(obj),
        )

    @admin.display(description=_('Courses'))
    def course_specializations_display(self, obj):
        labels = obj.get_course_type_labels()
        if not labels:
            return '—'
        return ', '.join(labels)

    @admin.display(description=_('Preview'))
    def profile_image_preview(self, obj):
        return _profile_image_preview(obj)

    @admin.display(description=_('Login'))
    def user_link(self, obj):
        if not obj.user_id:
            return '—'
        return format_html(
            '<span class="portal-person__sub">@{}</span>',
            obj.user.get_username(),
        )

    @admin.display(description='Groups')
    def group_count_display(self, obj):
        count = obj.groups.count()
        return portal_count_badge(count, 'groups', tone='blue')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        from portals.utils.teacher_courses import sync_teacher_specialization_text

        sync_teacher_specialization_text(form.instance.pk)


@admin.register(StudentProfile)
class StudentProfileAdmin(PortalModelAdmin):
    inlines = (StudentCourseSpecializationInline,)
    list_display = (
        'full_name_link',
        'person_display',
        'services_display',
        'groups_display',
        'phone',
        'enrollment_date',
        'role_chip',
    )
    list_display_links = ('full_name_link',)
    list_filter = (
        'course_specializations__course_type',
        'course_specializations__is_active',
        'groups',
        'enrollment_date',
    )
    search_fields = (
        'phone',
        'user__username',
        'user__email',
        'groups__name',
    )
    autocomplete_fields = ('user',)
    readonly_fields = ('profile_image_preview',)
    ordering = ('user__username', 'id')
    list_per_page = 25
    fieldsets = (
        (_('Account'), {
            'classes': ('portal-fieldset',),
            'description': _(
                'Pick an existing login account, or create one under Users with role '
                'Student — a profile is created automatically. Assign active service '
                'enrollments below — quizzes and classrooms follow those services. '
                'Study groups are for schedule and attendance only.'
            ),
            'fields': ('user',),
        }),
        (_('Personal information'), {
            'classes': ('portal-fieldset',),
            'fields': (
                'profile_image',
                'profile_image_preview',
                'phone',
                'bio',
                'enrollment_date',
            ),
        }),
        (_('Social media'), {
            'classes': ('portal-fieldset',),
            'fields': ('instagram', 'facebook', 'linkedin', 'youtube'),
        }),
    )

    def get_portal_stats(self, request):
        total = StudentProfile.objects.count()
        no_group = (
            StudentProfile.objects.annotate(_g=Count('groups'))
            .filter(_g=0)
            .count()
        )
        return [
            {'value': total, 'label': _('Students'), 'tone': 'purple'},
            {'value': no_group, 'label': _('Without group'), 'tone': 'amber'},
        ]

    @admin.display(description=_('Services'))
    def services_display(self, obj):
        labels = obj.get_course_type_labels()
        if not labels:
            return '—'
        return ', '.join(labels)

    @admin.display(description=_('Groups'))
    def groups_display(self, obj):
        names = list(obj.groups.values_list('name', flat=True)[:3])
        if not names:
            return format_html('<span class="portal-person__sub">—</span>')
        extra = obj.groups.count() - len(names)
        text = ', '.join(names)
        if extra > 0:
            text = f'{text} +{extra}'
        return format_html('<span class="portal-person__sub">{}</span>', text)

    @admin.display(description=_('Student'))
    def full_name_link(self, obj):
        return obj.full_name

    @admin.display(description=_('Student'))
    def person_display(self, obj):
        groups = obj.groups.count()
        subtitle = _('%(count)s group(s)') % {'count': groups} if groups else _('No group')
        return portal_person_cell(
            obj.full_name,
            subtitle=subtitle,
            role='student',
            photo_url=_profile_photo_url(obj),
        )

    @admin.display(description='Preview')
    def profile_image_preview(self, obj):
        return _profile_image_preview(obj)

    @admin.display(description='Role')
    def role_chip(self, obj):
        return portal_role_badge('Student', 'student')


@admin.register(ParentProfile)
class ParentProfileAdmin(PortalModelAdmin):
    list_display = (
        'full_name_link',
        'person_display',
        'linked_students_display',
        'phone',
        'role_chip',
    )
    list_display_links = ('full_name_link',)
    search_fields = (
        'phone',
        'user__username',
        'user__email',
        'students__user__username',
    )
    autocomplete_fields = ('user',)
    filter_horizontal = ('students',)
    ordering = ('user__username', 'id')
    list_per_page = 25
    fieldsets = (
        ('Account & children', {
            'classes': ('portal-fieldset',),
            'description': 'Parent sees attendance, scores, and quizzes for linked students only.',
            'fields': ('user', 'students'),
        }),
        ('Personal information', {
            'classes': ('portal-fieldset',),
            'fields': ('phone',),
        }),
    )

    def get_portal_stats(self, request):
        return [
            {
                'value': ParentProfile.objects.count(),
                'label': 'Parents',
                'tone': 'purple',
            },
        ]

    @admin.display(description='Parent')
    def full_name_link(self, obj):
        return obj.full_name

    @admin.display(description='Parent')
    def person_display(self, obj):
        children = obj.students.count()
        subtitle = _('%(count)s linked student(s)') % {'count': children} if children else _('No children linked')
        return portal_person_cell(
            obj.full_name,
            subtitle=subtitle,
            role='parent',
        )

    @admin.display(description='Linked students')
    def linked_students_display(self, obj):
        usernames = list(
            obj.students.select_related('user')
            .order_by('user__username')
            .values_list('user__username', flat=True)[:5]
        )
        if not usernames:
            return '—'
        text = ', '.join(usernames)
        extra = obj.students.count() - len(usernames)
        if extra > 0:
            text = f'{text} +{extra}'
        return text

    @admin.display(description='Role')
    def role_chip(self, obj):
        return portal_role_badge('Parent', 'parent')


@admin.register(CustomerProfile)
class CustomerProfileAdmin(PortalModelAdmin):
    list_display = (
        'full_name_link',
        'person_display',
        'teacher_display',
        'ielts_mock_credits',
        'sat_mock_credits',
        'phone',
        'role_chip',
    )
    list_display_links = ('full_name_link',)
    search_fields = ('phone', 'user__username', 'user__email', 'teacher__user__username')
    autocomplete_fields = ('user', 'teacher')
    ordering = ('user__username', 'id')
    list_per_page = 25
    fieldsets = (
        (_('Account'), {
            'classes': ('portal-fieldset',),
            'description': _(
                'Pick an existing login account, or create one under Authentication → Users '
                'with role Customer — username, password, and profile are created together.'
            ),
            'fields': ('user',),
        }),
        (_('Personal information'), {
            'classes': ('portal-fieldset',),
            'fields': ('phone', 'ielts_mock_credits', 'sat_mock_credits', 'teacher'),
        }),
    )

    def get_portal_stats(self, request):
        return [
            {
                'value': CustomerProfile.objects.count(),
                'label': _('Customers'),
                'tone': 'purple',
            },
        ]

    @admin.display(description=_('Customer'))
    def full_name_link(self, obj):
        return obj.full_name

    @admin.display(description=_('Customer'))
    def person_display(self, obj):
        subtitle = _('IELTS: %(ielts)s, SAT: %(sat)s') % {
            'ielts': obj.ielts_mock_credits,
            'sat': obj.sat_mock_credits,
        }
        return portal_person_cell(
            obj.full_name,
            subtitle=subtitle,
            role='customer',
        )

    @admin.display(description=_('Reviewing teacher'))
    def teacher_display(self, obj):
        if not obj.teacher_id:
            return '—'
        return portal_admin_change_link(obj.teacher, obj.teacher.full_name)

    @admin.display(description='Role')
    def role_chip(self, obj):
        return portal_role_badge('Customer', 'customer')


# ---------------------------------------------------------------------------
# Groups & schedule
# ---------------------------------------------------------------------------

class StudyGroupAdminForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        teacher = cleaned.get('teacher')
        course_ids = self.data.getlist('courses')
        codes = portal_codes_for_service_ids(course_ids)
        if teacher and codes and not teacher_has_all_course_codes(teacher.pk, codes):
            self.add_error(
                'teacher',
                _('This teacher is not assigned to all selected courses.'),
            )
        return cleaned


@admin.register(StudyGroup)
class StudyGroupAdmin(CourseTypeTabFilterMixin, PortalModelAdmin):
    form = StudyGroupAdminForm
    list_display = (
        'name',
        'teacher_display',
        'courses_display',
        'capacity_display',
        'is_active',
    )
    list_display_links = ('name',)
    list_filter = ('is_active', 'courses', 'teacher')
    search_fields = ('name', 'teacher__user__username', 'courses__slug')
    autocomplete_fields = ('teacher',)
    filter_horizontal = ('courses', 'students')
    list_editable = ('is_active',)
    ordering = ('-is_active', 'name', 'id')
    list_per_page = 25
    inlines = (ScheduleInline,)
    fieldsets = (
        ('Group basics', {
            'classes': ('portal-fieldset',),
            'description': _('Name, linked courses, teacher, and active status.'),
            'fields': ('name', 'courses', 'teacher', 'is_active'),
        }),
        ('Course details', {
            'classes': ('portal-fieldset',),
            'description': _(
                'Students inherit the course from the group you create — pick the matching '
                'course(s) above. Only teachers assigned to those courses can be selected.'
            ),
            'fields': ('start_date', 'max_students'),
        }),
        ('Students', {
            'classes': ('portal-fieldset',),
            'description': _(
                'Only students with a matching active service enrollment (or no enrollments yet) '
                'are listed. A student can belong to more than one group.'
            ),
            'fields': ('students',),
        }),
    )

    class Media(PortalModelAdmin.Media):
        js = PortalModelAdmin.Media.js + ('portals/admin/js/study_group_admin.js',)

    def get_queryset(self, request):
        qs = admin.ModelAdmin.get_queryset(self, request)
        qs = qs.select_related('teacher').prefetch_related('courses').annotate(
            _student_count=Count('students', distinct=True),
        )
        course_type = request.GET.get(self.course_type_query_param)
        if course_type:
            slugs = expand_course_types_to_service_slugs([course_type])
            qs = qs.filter(courses__slug__in=slugs).distinct() if slugs else qs.none()
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'teacher':
            obj_id = request.resolver_match.kwargs.get('object_id')
            codes = []
            if obj_id:
                group = StudyGroup.objects.filter(pk=obj_id).prefetch_related('courses').first()
                if group:
                    codes = study_group_portal_codes(group)
            if codes:
                kwargs['queryset'] = teachers_for_portal_course_codes(codes)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'courses':
            kwargs['queryset'] = get_active_services_queryset()
        if db_field.name == 'students':
            obj_id = request.resolver_match.kwargs.get('object_id')
            group = None
            if obj_id:
                group = StudyGroup.objects.filter(pk=obj_id).prefetch_related('courses').first()
            kwargs['queryset'] = students_matching_group_courses(group)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def get_portal_stats(self, request):
        active = StudyGroup.objects.filter(is_active=True).count()
        students = (
            StudentProfile.objects.filter(groups__isnull=False)
            .distinct()
            .count()
        )
        return [
            {'value': active, 'label': 'Active groups', 'tone': 'purple'},
            {'value': students, 'label': 'Enrolled students', 'tone': 'teal'},
        ]

    @admin.display(description=_('Teacher'))
    def teacher_display(self, obj):
        if not obj.teacher_id:
            return '—'
        return portal_admin_change_link(obj.teacher, obj.teacher.full_name)

    @admin.display(description=_('Courses'))
    def courses_display(self, obj):
        if not obj or not obj.pk:
            return _('Select course(s) when creating the group.')
        if hasattr(obj, '_prefetched_objects_cache') and 'courses' in obj._prefetched_objects_cache:
            courses = list(obj.courses.all())
        else:
            courses = list(obj.courses.all())
        if not courses:
            return '—'
        from portals.utils.portal_services import infer_course_type_for_service, localized_service_name

        pills = [
            portal_course_pill(
                infer_course_type_for_service(course) or course.slug or '',
                localized_service_name(course),
            )
            for course in courses
        ]
        return format_html(' '.join('{}' for _ in pills), *pills)

    @admin.display(description='Capacity')
    def capacity_display(self, obj):
        count = getattr(obj, '_student_count', obj.students.count())
        return portal_capacity_bar(count, obj.max_students)


@admin.register(Schedule)
class ScheduleAdmin(PortalModelAdmin):
    list_display = (
        'group_display',
        'weekday_display',
        'start_time',
        'duration_min',
        'effective_from',
        'room_or_link_short',
    )
    list_display_links = ('group_display',)
    list_filter = ('weekday', 'group', 'group__courses')
    search_fields = ('group__name', 'room_or_link')
    autocomplete_fields = ('group',)
    ordering = ('group', 'weekday', 'start_time', 'id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'description': (
                'One recurring weekly slot. When marking attendance, always pick '
                'the schedule slot AND the actual session date.'
            ),
            'fields': ('group', 'weekday', 'start_time', 'duration_min', 'room_or_link', 'effective_from'),
        }),
    )

    @admin.display(description=_('Group'))
    def group_display(self, obj):
        if not obj.group_id:
            return '—'
        return portal_admin_change_link(obj.group, obj.group.name)

    @admin.display(description='Day')
    def weekday_display(self, obj):
        return portal_day_badge(obj.get_weekday_display())

    @admin.display(description='Room / link')
    def room_or_link_short(self, obj):
        text = obj.room_or_link or '—'
        if len(text) > 40:
            return f'{text[:40]}…'
        return text


# ---------------------------------------------------------------------------
# Lessons & videos
# ---------------------------------------------------------------------------

class LessonCategoryAdminForm(forms.ModelForm):
    class Meta:
        model = LessonCategory
        fields = ('service', 'name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = list(get_active_course_type_choices())
        existing = getattr(self.instance, 'service', None)
        if existing and existing not in {code for code, _ in choices}:
            choices = [(existing, resolve_course_type_label(existing)), *choices]
        self.fields['service'] = forms.ChoiceField(
            label=_('Service'),
            choices=choices,
            required=True,
        )


@admin.register(LessonCategory)
class LessonCategoryAdmin(CourseTypeTabFilterMixin, PortalModelAdmin):
    form = LessonCategoryAdminForm
    course_type_field = 'service'

    list_display = ('name', 'service_display', 'lesson_count_display')
    list_display_links = ('name',)
    list_filter = ('service',)
    search_fields = ('name', 'service')
    ordering = ('service', 'name', 'id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': ('service', 'name'),
        }),
    )

    @admin.display(description=_('Service'), ordering='service')
    def service_display(self, obj):
        return portal_course_pill(resolve_course_type_label(obj.service))

    @admin.display(description=_('Lessons'))
    def lesson_count_display(self, obj):
        return portal_count_badge(obj.lessons.count())


@admin.register(Lesson)
class LessonAdmin(PortalModelAdmin):
    list_display = (
        'name',
        'subject',
        'category',
        'group_display',
        'teacher_display',
        'lesson_date',
        'has_materials',
        'created_at',
    )
    list_display_links = ('name',)
    list_filter = ('subject', 'category', 'group', 'teacher', 'lesson_date', 'created_at')
    search_fields = ('name', 'description', 'group__name', 'category__name')
    autocomplete_fields = ('group', 'teacher', 'category')
    readonly_fields = ('created_at',)
    ordering = ('-lesson_date', '-created_at', 'id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'description': _('Lesson materials visible to students in the selected group.'),
            'fields': ('name', 'subject', 'category', 'group', 'teacher', 'lesson_date'),
        }),
        (_('Content'), {
            'fields': ('description', 'pdf_file', 'video_url', 'image'),
        }),
        (_('Date'), {
            'fields': ('created_at',),
        }),
    )

    @admin.display(description=_('Materials'), boolean=True)
    def has_materials(self, obj):
        return bool(obj.pdf_file or obj.video_url or obj.image)

    @admin.display(description=_('Group'))
    def group_display(self, obj):
        if not obj.group_id:
            return '—'
        return portal_admin_change_link(obj.group, obj.group.name)

    @admin.display(description=_('Teacher'))
    def teacher_display(self, obj):
        if not obj.teacher_id:
            return '—'
        return portal_admin_change_link(obj.teacher, obj.teacher.full_name)


@admin.register(Classroom)
class ClassroomAdmin(PortalModelAdmin):
    service_tab_query_param = 'service'
    list_display = ('name', 'group', 'teacher', 'has_pdf', 'created_at')
    list_display_links = ('name',)
    list_filter = ('services', 'created_at')
    search_fields = ('name', 'description', 'services__slug', 'services__name_az')
    filter_horizontal = ('services',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at', 'id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'description': _(
                'Group textbooks with PDF files. Teachers create these in the portal; '
                'only students in the selected group can see them.',
            ),
            'fields': ('name', 'description', 'pdf_file', 'group', 'teacher', 'services'),
        }),
        (_('System'), {
            'fields': ('created_at',),
        }),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'services':
            from portals.utils.portal_services import get_active_services_queryset

            kwargs['queryset'] = get_active_services_queryset()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related('services')
        slug = request.GET.get(self.service_tab_query_param)
        if slug:
            qs = qs.filter(services__slug=slug, services__is_active=True).distinct()
        return qs

    def _service_tab_url(self, request, slug):
        params = request.GET.copy()
        if slug:
            params[self.service_tab_query_param] = slug
        else:
            params.pop(self.service_tab_query_param, None)
        changelist_url = reverse(
            f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist',
        )
        query = params.urlencode()
        return f'{changelist_url}?{query}' if query else changelist_url

    def get_service_tabs(self, request):
        from portals.utils.portal_services import get_active_services_queryset, localized_service_name

        current = request.GET.get(self.service_tab_query_param, '')
        tabs = [{
            'label': _('All'),
            'url': self._service_tab_url(request, ''),
            'active': not current,
        }]
        for service in get_active_services_queryset():
            if not service.slug:
                continue
            tabs.append({
                'label': localized_service_name(service),
                'url': self._service_tab_url(request, service.slug),
                'active': current == service.slug,
            })
        return tabs

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['course_type_tabs'] = self.get_service_tabs(request)
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description=_('Services'))
    def services_display(self, obj):
        labels = obj.get_service_labels()
        if not labels:
            return '—'
        return ', '.join(labels)

    @admin.display(description=_('PDF'), boolean=True)
    def has_pdf(self, obj):
        return bool(obj.pdf_file)


@admin.register(VideoRecord)
class VideoRecordAdmin(PortalModelAdmin):
    list_display = ('title', 'group_display', 'lesson_date', 'youtube_url_short')
    list_display_links = ('title',)
    list_filter = ('group', 'lesson_date')
    search_fields = ('title', 'description', 'group__name')
    autocomplete_fields = ('group',)
    date_hierarchy = 'lesson_date'
    ordering = ('-lesson_date', '-id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'description': 'Past class recording on YouTube for students in this group.',
            'fields': ('group', 'title', 'lesson_date', 'youtube_url'),
        }),
        ('Description', {
            'fields': ('description',),
        }),
    )

    @admin.display(description=_('Group'))
    def group_display(self, obj):
        if not obj.group_id:
            return '—'
        return portal_admin_change_link(obj.group, obj.group.name)

    @admin.display(description='YouTube')
    def youtube_url_short(self, obj):
        url = obj.youtube_url or ''
        if len(url) > 45:
            return f'{url[:45]}…'
        return url


# ---------------------------------------------------------------------------
# Attendance & scores
# ---------------------------------------------------------------------------

@admin.register(Attendance)
class AttendanceAdmin(PortalModelAdmin):
    list_display = (
        'student_display',
        'schedule_display',
        'session_date',
        'status_badge',
        'marked_at',
    )
    list_display_links = ('student_display',)
    list_filter = ('status', 'session_date', 'schedule__group')
    search_fields = (
        'student__user__username',
        'schedule__group__name',
        'note',
    )
    autocomplete_fields = ('schedule', 'student')
    date_hierarchy = 'session_date'
    ordering = ('-session_date', '-marked_at', 'id')
    list_per_page = 25
    fieldsets = (
        ('Session', {
            'classes': ('portal-fieldset',),
            'description': (
                'Pick schedule slot, student, real session date, and status.'
            ),
            'fields': ('schedule', 'student', 'session_date', 'status'),
        }),
        ('Notes', {
            'classes': ('portal-fieldset',),
            'fields': ('note', 'marked_at'),
        }),
    )
    readonly_fields = ('marked_at',)

    @admin.display(description=_('Student'))
    def student_display(self, obj):
        if not obj.student_id:
            return '—'
        return portal_admin_change_link(obj.student, obj.student.full_name)

    @admin.display(description=_('Schedule'))
    def schedule_display(self, obj):
        if not obj.schedule_id:
            return '—'
        label = f'{obj.schedule.group.name} — {obj.schedule.get_weekday_display()} {obj.schedule.start_time:%H:%M}'
        return portal_admin_change_link(obj.schedule, label)

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            Attendance.Status.PRESENT: ('green', 'Present'),
            Attendance.Status.ABSENT: ('red', 'Absent'),
            Attendance.Status.LATE: ('yellow', 'Late'),
        }
        css, label = colors.get(obj.status, ('gray', obj.get_status_display()))
        return format_html(
            '<span class="admin-badge admin-badge--{}">{}</span>',
            css,
            label,
        )


@admin.register(Score)
class ScoreAdmin(PortalModelAdmin):
    list_display = (
        'student_display',
        'score_type',
        'score_display',
        'date',
        'lesson_display',
    )
    list_display_links = ('student_display',)
    list_filter = ('score_type', 'date', 'student__groups')
    search_fields = (
        'student__user__username',
        'comment',
        'lesson__name',
    )
    autocomplete_fields = ('student', 'lesson')
    list_select_related = ('student__user', 'lesson')
    date_hierarchy = 'date'
    ordering = ('-date', '-id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'description': (
                'Grade or score for a student. Visible to the student, their parents, '
                'and teachers in the portal.'
            ),
            'fields': ('student', 'score_type', 'lesson'),
        }),
        ('Result', {
            'fields': ('value', 'max_value', 'date', 'comment'),
        }),
    )

    @admin.display(description='Score')
    def score_display(self, obj):
        return portal_score_chip(obj.value, obj.max_value)

    @admin.display(description=_('Student'))
    def student_display(self, obj):
        if not obj.student_id:
            return '—'
        return portal_admin_change_link(obj.student, obj.student.full_name)

    @admin.display(description=_('Lesson'))
    def lesson_display(self, obj):
        if not obj.lesson_id:
            return '—'
        return portal_admin_change_link(obj.lesson, obj.lesson.display_name)


@admin.register(WeeklyStudentScore)
class WeeklyStudentScoreAdmin(PortalModelAdmin):
    list_display = (
        'student_display',
        'teacher_display',
        'study_group',
        'week_start',
        'score_display',
        'updated_at',
    )
    list_display_links = ('student_display',)
    list_filter = ('week_start', 'teacher', 'student__groups')
    search_fields = (
        'student__user__username',
        'teacher__user__username',
        'comment',
    )
    autocomplete_fields = ('student', 'teacher', 'study_group')
    date_hierarchy = 'week_start'
    ordering = ('-week_start', '-updated_at', '-id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'description': _(
                'Weekly score out of 10 for a student. Teachers can also enter '
                'scores from the portal weekly scores page.'
            ),
            'fields': ('student', 'teacher', 'study_group', 'week_start'),
        }),
        ('Result', {
            'fields': ('score', 'comment', 'created_at', 'updated_at'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description='Score')
    def score_display(self, obj):
        return portal_score_chip(float(obj.score), WEEKLY_SCORE_MAX)

    @admin.display(description=_('Student'))
    def student_display(self, obj):
        if not obj.student_id:
            return '—'
        return portal_admin_change_link(obj.student, obj.student.full_name)

    @admin.display(description=_('Teacher'))
    def teacher_display(self, obj):
        if not obj.teacher_id:
            return '—'
        return portal_admin_change_link(obj.teacher, obj.teacher.full_name)


# ---------------------------------------------------------------------------
# Quizzes
# ---------------------------------------------------------------------------

class QuizCategoryAdminForm(forms.ModelForm):
    class Meta:
        model = QuizCategory
        fields = ('services', 'name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['services'].queryset = get_active_services_queryset()
        self.fields['services'].required = True

    def clean_services(self):
        services = self.cleaned_data.get('services')
        if not services:
            raise forms.ValidationError(_('Select at least one active site service.'))
        return services


@admin.register(QuizCategory)
class QuizCategoryAdmin(CourseTypeTabFilterMixin, PortalModelAdmin):
    form = QuizCategoryAdminForm

    list_display = ('name', 'service_display', 'quiz_count_display')
    list_display_links = ('name',)
    list_filter = ('services',)
    search_fields = ('name', 'services__slug', 'services__name_az', 'services__name_en')
    filter_horizontal = ('services',)
    ordering = ('name', 'id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'description': _(
                'Quiz categories group quizzes under linked site services. '
                'Teachers and students reach quizzes indirectly through category services.'
            ),
            'fields': ('services', 'name'),
        }),
    )
    inlines = ()

    def get_queryset(self, request):
        qs = admin.ModelAdmin.get_queryset(self, request)
        qs = qs.prefetch_related('services').annotate(_quiz_count=Count('quizzes', distinct=True))
        course_type = request.GET.get(self.course_type_query_param)
        if course_type:
            slugs = expand_course_types_to_service_slugs([course_type])
            qs = qs.filter(services__slug__in=slugs).distinct() if slugs else qs.none()
        return qs

    @admin.display(description=_('Services'))
    def service_display(self, obj):
        services = list(obj.services.all())
        if not services:
            return '—'
        from portals.utils.portal_services import infer_course_type_for_service, localized_service_name

        return ', '.join(
            portal_course_pill(
                infer_course_type_for_service(service) or service.slug or '',
                localized_service_name(service),
            )
            for service in services
        )

    @admin.display(description=_('Quizzes'))
    def quiz_count_display(self, obj):
        count = getattr(obj, '_quiz_count', obj.quizzes.count())
        return portal_count_badge(count, 'quizzes', tone='blue')


class QuizAdminForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = (
            'category',
            'topic',
            'is_listening',
            'is_essay',
            'is_speaking',
            'is_reading',
            'is_math',
            'is_ielts',
            'is_sat',
            'sat_section',
            'is_time_limited',
            'time_limit_minutes',
        )
        widgets = {
            'sat_section': forms.RadioSelect,
        }

    def clean(self):
        cleaned = super().clean()

        if cleaned.get('is_sat'):
            sat_section = cleaned.get('sat_section') or ''
            if not sat_section:
                self.add_error(
                    'sat_section',
                    _('Select a SAT section type (Reading, Writing, Algebra, or Geometry & Data).'),
                )
            elif sat_section not in dict(Quiz.SatSection.choices):
                self.add_error('sat_section', _('Invalid SAT section type.'))
            else:
                cleaned['is_listening'] = False
                cleaned['is_speaking'] = False
                cleaned['is_essay'] = False
                cleaned['is_math'] = False
                cleaned['is_reading'] = sat_section == Quiz.SatSection.READING
        else:
            cleaned['sat_section'] = ''
            cleaned['is_math'] = False

        if not cleaned.get('is_sat'):
            cleaned['is_math'] = False

        format_flags = [
            cleaned.get('is_listening'),
            cleaned.get('is_essay'),
            cleaned.get('is_speaking'),
            cleaned.get('is_reading'),
            cleaned.get('is_math'),
        ]
        if sum(1 for flag in format_flags if flag) > 1:
            raise forms.ValidationError(
                _('Only one quiz format can be enabled (Listening, Essay, Speaking, Reading, or Math).'),
            )

        if cleaned.get('is_math') and not cleaned.get('is_sat'):
            self.add_error(
                'is_math',
                _('Math format is only available when SAT is enabled.'),
            )

        if cleaned.get('is_ielts') and cleaned.get('is_sat'):
            raise forms.ValidationError(
                _('Select only one mock test program: IELTS or SAT.'),
            )

        if cleaned.get('is_speaking'):
            cleaned['is_time_limited'] = False
            cleaned['time_limit_minutes'] = None
        elif cleaned.get('is_time_limited'):
            minutes = cleaned.get('time_limit_minutes')
            if not minutes or minutes < 1:
                self.add_error(
                    'time_limit_minutes',
                    _('Enter the time limit in minutes (at least 1).'),
                )
        else:
            cleaned['time_limit_minutes'] = None

        return cleaned


@admin.register(Quiz)
class QuizAdmin(CourseTypeTabFilterMixin, PortalModelAdmin):
    form = QuizAdminForm

    class Media:
        css = {'all': ('portals/css/quiz-question-admin.css',)}
        js = ('portals/admin/js/quiz-question-admin.js',)

    list_display = (
        'topic',
        'category_display',
        'grading_mode_display',
        'service_display',
        'question_count',
        'created_at',
    )
    list_display_links = ('topic',)
    list_filter = ('category', 'category__services', 'is_ielts', 'is_sat', 'sat_section', 'created_at')
    search_fields = ('topic', 'category__name', 'category__services__slug')
    autocomplete_fields = ('category',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at', 'id')
    list_per_page = 25
    inlines = (QuizQuestionInline,)
    fieldsets = (
        (None, {
            'description': (
                'Pick a category — service comes from the category. '
                'Teachers and students see quizzes when their assigned service '
                'matches the category service.'
            ),
            'fields': ('category', 'topic', 'created_at'),
        }),
        (_('Grading mode'), {
            'description': _(
                'Enable at most one format. Listening, Essay, and Speaking are teacher-reviewed. '
                'Reading is auto-scored with passages and structured questions. '
                'Math appears when SAT is enabled and uses the same passage/question layout as Reading. '
                'Leave all unchecked for standard multiple-choice variant quizzes.'
            ),
            'fields': ('is_listening', 'is_essay', 'is_speaking', 'is_reading', 'is_math'),
            'classes': ('quiz-grading-fieldset',),
        }),
        (_('Exam program'), {
            'description': _(
                'Mark the exam program this quiz belongs to. '
                'When SAT is enabled, choose a SAT section type below — Reading uses IELTS-style passages.'
            ),
            'fields': ('is_ielts', 'is_sat'),
        }),
        (_('SAT section'), {
            'description': _(
                'Required when SAT is enabled. Pick exactly one section: '
                'Reading (passage-based), Writing, Algebra, or Geometry & Data (multiple choice).'
            ),
            'fields': ('sat_section',),
            'classes': ('sat-section-fieldset',),
        }),
        (_('Time limit'), {
            'description': _('Optional countdown — auto-submits when time runs out.'),
            'fields': ('is_time_limited', 'time_limit_minutes'),
        }),
        (_('Resource import'), {
            'description': _(
                'When loaded from JSON resources, resource_slug is set automatically. '
                'Questions are stored as inline quiz questions below.'
            ),
            'fields': ('resource_slug',),
        }),
    )

    def get_inlines(self, request, obj=None):
        if obj and obj.is_listening:
            return (ListeningAudioInline,)
        if obj and (obj.is_reading or obj.is_math):
            return (ReadingPassageInline,)
        if obj and obj.is_speaking:
            return (SpeakingPartInline,)
        if obj is None and self._quiz_format_flag(request, 'is_speaking'):
            return (SpeakingPartInline,)
        if obj is None and self._quiz_format_flag(request, 'is_listening'):
            return (ListeningAudioInline,)
        if obj is None and (
            self._quiz_format_flag(request, 'is_reading')
            or self._quiz_format_flag(request, 'is_math')
        ):
            return (ReadingPassageInline,)
        return (QuizQuestionInline,)

    def _quiz_format_flag(self, request, name: str) -> bool:
        return request.POST.get(name) in ('on', 'true', 'True', '1')

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'grading-mode-fields/',
                self.admin_site.admin_view(self.grading_mode_fields_view),
                name='portals_quiz_grading_mode_fields',
            ),
            path(
                'sat-section-config/',
                self.admin_site.admin_view(self.sat_section_config_view),
                name='portals_quiz_sat_section_config',
            ),
        ]
        return custom + urls

    def grading_mode_fields_view(self, request):
        if request.method != 'POST':
            return JsonResponse({'error': _('POST required.')}, status=405)

        def _flag(name):
            return request.POST.get(name) in ('on', 'true', 'True', '1')

        is_essay = _flag('is_essay')
        is_listening = _flag('is_listening')
        is_speaking = _flag('is_speaking')
        is_reading = _flag('is_reading')
        is_math = _flag('is_math')

        if is_essay:
            mode = 'essay'
        elif is_listening:
            mode = 'listening'
        elif is_speaking:
            mode = 'speaking'
        elif is_math:
            mode = 'math'
        elif is_reading:
            mode = 'reading'
        else:
            mode = 'variant'

        answer_fields = ('answer_options', 'correct_answer')
        response_field = 'student_response_preview'

        if mode == 'essay':
            show_fields = [response_field]
            hide_fields = list(answer_fields)
            clear_fields = list(answer_fields)
        elif mode == 'variant':
            show_fields = list(answer_fields)
            hide_fields = [response_field]
            clear_fields = []
        elif mode in ('reading', 'math'):
            show_fields = []
            hide_fields = [*answer_fields, response_field]
            clear_fields = list(answer_fields)
        else:
            show_fields = []
            hide_fields = [*answer_fields, response_field]
            clear_fields = list(answer_fields)

        return JsonResponse({
            'grading_mode': mode,
            'show_fields': show_fields,
            'hide_fields': hide_fields,
            'clear_fields': clear_fields,
            'hide_time_limit': mode == 'speaking',
        })

    def sat_section_config_view(self, request):
        if request.method != 'POST':
            return JsonResponse({'error': _('POST required.')}, status=405)

        is_sat = request.POST.get('is_sat') in ('on', 'true', 'True', '1')
        sat_section = (request.POST.get('sat_section') or '').strip()

        if not is_sat:
            return JsonResponse({
                'is_sat': False,
                'grading_mode': 'variant',
                'flags': {
                    'is_listening': False,
                    'is_essay': False,
                    'is_speaking': False,
                    'is_reading': False,
                    'is_math': False,
                },
            })

        flags = {
            'is_listening': False,
            'is_essay': False,
            'is_speaking': False,
            'is_reading': sat_section == Quiz.SatSection.READING,
            'is_math': False,
        }
        if sat_section == Quiz.SatSection.READING:
            grading_mode = 'reading'
        else:
            grading_mode = 'variant'

        return JsonResponse({
            'is_sat': True,
            'sat_section': sat_section,
            'grading_mode': grading_mode,
            'flags': flags,
        })

    @admin.display(description=_('Mode'))
    def grading_mode_display(self, obj):
        return obj.get_grading_mode_label()

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if (
            request.GET.get('app_label') == 'portals'
            and request.GET.get('field_name') == 'quiz'
        ):
            model_name = request.GET.get('model_name')
            if model_name == 'listeningaudio':
                queryset = queryset.filter(is_listening=True)
            elif model_name == 'readingpassage':
                queryset = queryset.filter(Q(is_reading=True) | Q(is_math=True))
            elif model_name == 'speakingpart':
                queryset = queryset.filter(is_speaking=True)
        return queryset, use_distinct

    def get_queryset(self, request):
        qs = admin.ModelAdmin.get_queryset(self, request)
        qs = qs.annotate(_question_count=Count('questions', distinct=True)).select_related(
            'category',
        ).prefetch_related('category__services')
        course_type = request.GET.get(self.course_type_query_param)
        if course_type:
            slugs = expand_course_types_to_service_slugs([course_type])
            qs = qs.filter(category__services__slug__in=slugs).distinct() if slugs else qs.none()
        return qs

    @admin.display(description='Questions')
    def question_count(self, obj):
        if obj.is_reading or obj.is_math:
            from portals.utils.quiz_reading import get_reading_questions_for_quiz

            count = len(get_reading_questions_for_quiz(obj))
        elif obj.is_speaking:
            from portals.utils.quiz_speaking import get_speaking_questions_for_quiz

            count = len(get_speaking_questions_for_quiz(obj))
        elif obj.is_listening:
            from portals.utils.quiz_listening import get_listening_questions_for_quiz

            count = len(get_listening_questions_for_quiz(obj))
        else:
            count = getattr(obj, '_question_count', obj.questions.count())
        return portal_count_badge(count, 'questions', tone='teal')

    @admin.display(description=_('Category'))
    def category_display(self, obj):
        if not obj.category_id:
            return '—'
        return portal_admin_change_link(obj.category, obj.category.name)

    @admin.display(description=_('Services'))
    def service_display(self, obj):
        if not obj.category_id:
            return '—'
        from portals.utils.portal_services import localized_service_name

        labels = [localized_service_name(service) for service in obj.category.services.all()]
        if not labels:
            return '—'
        return ', '.join(portal_course_pill(label, 'default') for label in labels)



@admin.register(QuizQuestion)
class QuizQuestionAdmin(PortalModelAdmin):
    form = QuizQuestionAdminForm
    list_display = ('question_short', 'quiz_display', 'order', 'prompt_type', 'option_count')
    list_display_links = ('question_short',)
    list_filter = ('prompt_type', 'quiz')
    search_fields = ('question', 'quiz__topic', 'correct_answer')
    autocomplete_fields = ('quiz',)
    ordering = ('quiz', 'order', 'id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'description': _(
                'Pick question type — the form switches instantly between text, image, video, or audio.',
            ),
            'fields': ('quiz', 'order', 'prompt_type', 'question', 'media_file', 'media_url'),
        }),
        (_('Answers'), {
            'description': _('Answer options as JSON list. Correct answer must match one option exactly.'),
            'fields': ('answer_options', 'correct_answer'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if obj and obj.quiz_id and obj.quiz.is_essay:
            fieldsets[1] = (
                _('Student response'),
                {
                    'description': _(
                        'Essay quizzes have no multiple-choice options. '
                        'Students type their answer in a text field during the quiz.',
                    ),
                    'fields': ('student_response_preview',),
                },
            )
        elif obj and obj.quiz_id and obj.quiz.is_manual_grading:
            fieldsets = [fieldsets[0]]
        return fieldsets

    @admin.display(description=_('Quiz'))
    def quiz_display(self, obj):
        if not obj.quiz_id:
            return '—'
        return portal_admin_change_link(obj.quiz, obj.quiz.topic)

    @admin.display(description=_('Options'))
    def option_count(self, obj):
        return len(obj.answer_options or [])

    @admin.display(description='Question')
    def question_short(self, obj):
        text = obj.question or ''
        if len(text) > 60:
            return f'{text[:60]}…'
        return text


@admin.register(QuizResult)
class QuizResultAdmin(PortalModelAdmin):
    list_display = (
        'student_display',
        'quiz_display',
        'total_score',
        'review_status_display',
        'duration_display',
        'completed_at',
    )
    list_display_links = ('student_display',)
    list_filter = ('quiz', 'completed_at', 'student__groups')
    search_fields = (
        'student__user__username',
        'quiz__topic',
    )
    autocomplete_fields = ('student', 'quiz')
    list_select_related = ('student__user', 'quiz', 'quiz__category')
    readonly_fields = ('completed_at',)
    date_hierarchy = 'completed_at'
    ordering = ('-completed_at', 'id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'description': (
                'Variant quizzes are scored automatically. '
                'Listening / Essay / Speaking quizzes are reviewed by the teacher.'
            ),
            'fields': ('student', 'quiz', 'total_score', 'duration_sec', 'completed_at', 'reviewed_at'),
        }),
        (_('Student submission'), {
            'fields': ('student_submission', 'given_answers'),
        }),
        (_('Teacher review'), {
            'fields': ('teacher_feedback',),
        }),
    )

    @admin.display(description=_('Student'))
    def student_display(self, obj):
        if not obj.student_id:
            return '—'
        return portal_admin_change_link(obj.student, obj.student.full_name)

    @admin.display(description=_('Quiz'))
    def quiz_display(self, obj):
        if not obj.quiz_id:
            return '—'
        return portal_admin_change_link(obj.quiz, obj.quiz.topic)

    @admin.display(description=_('Review'))
    def review_status_display(self, obj):
        if not obj.quiz.is_manual_grading:
            return _('Auto-scored')
        if obj.is_pending_review:
            return _('Pending')
        return _('Reviewed')

    @admin.display(description='Duration')
    def duration_display(self, obj):
        minutes, seconds = divmod(obj.duration_sec, 60)
        if minutes:
            return f'{minutes}m {seconds}s'
        return f'{seconds}s'


@admin.register(PortalNotification)
class PortalNotificationAdmin(PortalModelAdmin):
    list_display = ('id', 'kind', 'student', 'teacher', 'parent', 'is_read', 'created_at')
    list_filter = ('kind', 'is_read')
    list_select_related = (
        'student__user',
        'teacher__user',
        'parent__user',
        'quiz_result',
        'ielts_mock_test',
        'lesson_homework',
    )
    search_fields = (
        'student__user__username',
        'teacher__user__username',
        'parent__user__username',
    )
    readonly_fields = ('created_at',)
    ordering = ('-created_at', '-id')


@admin.register(QuizAssignment)
class QuizAssignmentAdmin(PortalModelAdmin):
    list_display = ('student_display', 'quiz_display', 'is_active', 'assigned_by_display', 'assigned_at')
    list_filter = ('is_active', 'quiz__category__services')
    list_select_related = ('student__user', 'quiz__category', 'assigned_by__user')
    search_fields = (
        'student__user__username',
        'quiz__topic',
        'assigned_by__user__username',
    )
    autocomplete_fields = ('student', 'quiz', 'assigned_by')
    list_editable = ('is_active',)
    ordering = ('-assigned_at', '-id')

    @admin.display(description=_('Student'), ordering='student__user__username')
    def student_display(self, obj):
        return portal_person_cell(obj.student)

    @admin.display(description=_('Quiz'), ordering='quiz__topic')
    def quiz_display(self, obj):
        return obj.quiz.topic if obj.quiz_id else '—'

    @admin.display(description=_('Assigned by'), ordering='assigned_by__user__username')
    def assigned_by_display(self, obj):
        if not obj.assigned_by_id:
            return '—'
        return portal_person_cell(obj.assigned_by)


@admin.register(QuizResultReview)
class QuizResultReviewAdmin(PortalModelAdmin):
    list_display = ('id', 'result', 'reviewer', 'score', 'reviewed_at')
    list_select_related = ('result__student__user', 'result__quiz', 'reviewer__user')
    search_fields = ('result__student__user__username', 'reviewer__user__username')
    readonly_fields = ('reviewed_at',)
    ordering = ('-reviewed_at', '-id')


@admin.register(IeltsMockTestAttempt)
class IeltsMockTestAttemptAdmin(PortalModelAdmin):
    list_display = ('id', 'student', 'status', 'current_section', 'started_at', 'completed_at')
    list_filter = ('status', 'current_section')
    list_select_related = ('student__user',)
    readonly_fields = ('started_at', 'completed_at')
    ordering = ('-started_at', '-id')


@admin.register(SpeakingRecording)
class SpeakingRecordingAdmin(PortalModelAdmin):
    list_display = ('id', 'question', 'result', 'duration_sec')
    list_select_related = ('question', 'result__student__user', 'result__quiz')
    ordering = ('-id',)


@admin.register(LessonAttachment)
class LessonAttachmentAdmin(PortalModelAdmin):
    list_display = ('id', 'lesson', 'kind', 'file', 'video_url')
    list_select_related = ('lesson', 'lesson__group')
    list_filter = ('kind',)
    search_fields = ('lesson__name',)
    ordering = ('lesson_id', 'id')


@admin.register(LessonHomework)
class LessonHomeworkAdmin(PortalModelAdmin):
    list_display = (
        'id',
        'lesson',
        'student_display',
        'file_kind',
        'has_file',
        'submitted_at',
    )
    list_select_related = ('lesson', 'lesson__group', 'student', 'student__user')
    list_filter = ('file_kind', 'submitted_at')
    search_fields = (
        'lesson__name',
        'student__user__username',
        'original_filename',
        'text',
    )
    autocomplete_fields = ('lesson', 'student')
    readonly_fields = ('created_at', 'submitted_at')
    ordering = ('-submitted_at', 'id')

    @admin.display(description=_('Student'))
    def student_display(self, obj):
        if not obj.student_id:
            return '—'
        return portal_admin_change_link(obj.student, obj.student.full_name)

    @admin.display(description=_('File'), boolean=True)
    def has_file(self, obj):
        return bool(obj.file and obj.file.name)


# ---------------------------------------------------------------------------
# Admin sidebar order (portal app)
# ---------------------------------------------------------------------------

_prev_get_app_list = admin.site.get_app_list

PORTAL_MODEL_ORDER = {
    'TeacherProfile': 10,
    'StudentProfile': 20,
    'ParentProfile': 30,
    'CustomerProfile': 35,
    'StudyGroup': 40,
    'Schedule': 50,
    'Lesson': 60,
    'LessonCategory': 62,
    'Classroom': 65,
    'VideoRecord': 70,
    'Attendance': 80,
    'Score': 90,
    'WeeklyStudentScore': 92,
    'QuizCategory': 95,
    'ListeningAudio': 96,
    'ReadingPassage': 97,
    'Quiz': 100,
    'QuizQuestion': 110,
    'QuizResult': 120,
    'PortalNotification': 125,
    'QuizResultReview': 126,
    'IeltsMockTestAttempt': 127,
    'SpeakingRecording': 128,
    'LessonAttachment': 129,
    'LessonHomework': 130,
}


def _portal_get_app_list(request, app_label=None):
    app_list = _prev_get_app_list(request, app_label)
    for app in app_list:
        if app.get('app_label') == 'portals':
            app['models'].sort(
                key=lambda m: PORTAL_MODEL_ORDER.get(m.get('object_name'), 9999),
            )
    return app_list


admin.site.get_app_list = _portal_get_app_list

# Add portal section to admin index help (public site admin index).
try:
    from projects.admin import help_texts as site_help

    if not any(s.get('name') == 'Student portal' for s in site_help.ADMIN_INDEX_HELP['sections']):
        site_help.ADMIN_INDEX_HELP['sections'].append({
            'name': _('Student portal'),
            'items': _('Teachers, Students, Parents, Customers, Groups, Lessons, Attendance, Quizzes'),
            'desc': _(
                'Purple section in admin — private portal for teachers, students, '
                'parents, and customers (not on the public website).'
            ),
        })
except ImportError:
    pass

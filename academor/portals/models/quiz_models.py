from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _


class QuizCategory(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
        help_text=_('Lower numbers appear first in the portal quiz category list.'),
    )
    services = models.ManyToManyField(
        'projects.Service',
        related_name='quiz_categories',
        blank=True,
        verbose_name=_('Services'),
        help_text=_('Site courses linked to this quiz category.'),
        null=True,

    )

    class Meta:
        verbose_name = _('Quiz category')
        verbose_name_plural = _('Quiz categories')
        ordering = ('order', 'name', 'id')

    def __str__(self):
        return self.name

    def get_portal_course_codes(self):
        from portals.utils.quiz_category_services import quiz_category_portal_codes

        return quiz_category_portal_codes(self)


class Quiz(models.Model):
    """
    Quiz set. Individual questions live in QuizQuestion.
    Service access is indirect via category.
    """

    MANUAL_REVIEW_MAX_SCORE = 10

    category = models.ForeignKey(
        QuizCategory,
        on_delete=models.PROTECT,
        related_name='quizzes',
        verbose_name=_('Category'),
    )
    topic = models.CharField(
        max_length=255,
        verbose_name=_('Topic'),
    )
    is_listening = models.BooleanField(
        default=False,
        verbose_name=_('Listening (auto-scored)'),
        help_text=_(
            'Multiple-choice listening quiz scored automatically when the student submits. '
            'No multiple-choice variants — only one manual mode can be active.',
        ),
    )
    is_essay = models.BooleanField(
        default=False,
        verbose_name=_('Writing (manual review)'),
        help_text=_('Written work — teacher grades and replies with corrections.'),
    )
    is_speaking = models.BooleanField(
        default=False,
        verbose_name=_('Speaking (manual review)'),
        help_text=_('Speaking task — teacher grades and replies with corrections.'),
    )
    is_reading = models.BooleanField(
        default=False,
        verbose_name=_('Reading (auto-scored)'),
        help_text=_(
            'IELTS-style reading with passages and auto-scored answers. '
            'Only one quiz format can be active.',
        ),
    )
    is_math = models.BooleanField(
        default=False,
        verbose_name=_('Math (auto-scored)'),
        help_text=_(
            'SAT Math section — auto-scored with passages/questions like Reading. '
            'Only available when SAT is enabled. Choose this yourself; it is not set automatically.'
        ),
    )
    has_shared_passage = models.BooleanField(
        default=False,
        verbose_name=_('Shared passage layout'),
        help_text=_(
            'For standard multiple-choice quizzes only. When enabled, a fixed passage stays at the top '
            'and questions appear below (Reading-style layout). Leave off for plain question lists. '
            'Not used with Listening, Writing, Speaking, Reading, or Math formats.'
        ),
    )
    shared_passage = RichTextField(
        blank=True,
        verbose_name=_('Shared passage text'),
        help_text=_('Fixed text shown above all questions when shared passage layout is enabled.'),
    )
    shared_audio_file = models.FileField(
        upload_to='portals/quiz/shared-media/',
        blank=True,
        null=True,
        verbose_name=_('Shared audio file'),
        help_text=_('Optional audio shown with the shared passage.'),
    )
    shared_youtube_url = models.URLField(
        blank=True,
        verbose_name=_('Shared YouTube URL'),
        help_text=_('Optional YouTube video shown with the shared passage.'),
    )
    is_ielts = models.BooleanField(
        default=False,
        verbose_name=_('IELTS'),
        help_text=_('Marks this quiz as part of the IELTS exam program.'),
    )
    is_sat = models.BooleanField(
        default=False,
        verbose_name=_('SAT'),
        help_text=_('Marks this quiz as part of the SAT exam program.'),
    )

    class SatSection(models.TextChoices):
        READING = 'reading', _('Reading')
        WRITING = 'writing', _('Writing')
        ALGEBRA = 'algebra', _('Algebra')
        GEOMETRY_DATA = 'geometry_data', _('Geometry & Data')

    SAT_RW_SECTIONS = frozenset({SatSection.READING, SatSection.WRITING})
    SAT_MATH_SECTIONS = frozenset({SatSection.ALGEBRA, SatSection.GEOMETRY_DATA})

    sat_section = models.CharField(
        max_length=32,
        blank=True,
        choices=SatSection.choices,
        verbose_name=_('SAT section'),
        help_text=_(
            'Required for SAT quizzes. Pick exactly one: Reading, Writing, Algebra, or Geometry & Data. '
            'Reading uses IELTS-style passages; the others use multiple-choice questions.',
        ),
    )
    is_time_limited = models.BooleanField(
        default=False,
        verbose_name=_('Time limited'),
        help_text=_('When enabled, set a time limit in minutes for the student attempt.'),
    )
    time_limit_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Time limit (minutes)'),
        help_text=_('Required when time limited is enabled.'),
    )
    resource_slug = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
        verbose_name=_('Resource slug'),
        help_text=_('Stable key from the JSON resource file (e.g. a1_quiz_1). Set when loaded from resources.'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
        help_text=_('Lower numbers appear first within the category on the portal quiz list.'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')
        ordering = ('order', 'topic', 'id')
        constraints = [
            models.CheckConstraint(
                name='portals_quiz_format_at_most_one',
                condition=(
                    models.Q(is_listening=False) | models.Q(is_essay=False)
                ) & (
                    models.Q(is_listening=False) | models.Q(is_speaking=False)
                ) & (
                    models.Q(is_listening=False) | models.Q(is_reading=False)
                ) & (
                    models.Q(is_essay=False) | models.Q(is_speaking=False)
                ) & (
                    models.Q(is_essay=False) | models.Q(is_reading=False)
                ) & (
                    models.Q(is_speaking=False) | models.Q(is_reading=False)
                ) & (
                    models.Q(is_math=False) | models.Q(is_listening=False)
                ) & (
                    models.Q(is_math=False) | models.Q(is_essay=False)
                ) & (
                    models.Q(is_math=False) | models.Q(is_speaking=False)
                ) & (
                    models.Q(is_math=False) | models.Q(is_reading=False)
                ),
            ),
            models.UniqueConstraint(
                fields=('category', 'resource_slug'),
                condition=~models.Q(resource_slug=''),
                name='portals_quiz_category_resource_slug_uniq',
            ),
            models.CheckConstraint(
                condition=~models.Q(is_ielts=True, is_sat=True),
                name='portals_quiz_single_mock_program',
            ),
        ]

    def __str__(self):
        return self.topic

    @property
    def service_code(self):
        if not self.category_id:
            return ''
        from portals.utils.quiz_category_services import quiz_category_primary_portal_code

        category = getattr(self, 'category', None)
        if category is None:
            category = QuizCategory.objects.filter(pk=self.category_id).prefetch_related('services').first()
        return quiz_category_primary_portal_code(category)

    @property
    def is_manual_grading(self):
        return self.is_essay or self.is_speaking

    @property
    def requires_teacher_review(self):
        return self.is_manual_grading

    @property
    def is_reading_quiz(self):
        return self.is_reading or self.is_math

    @property
    def is_variant_quiz(self):
        return (
            not self.is_manual_grading
            and not self.is_reading
            and not self.is_math
            and not self.is_listening
        )

    @property
    def uses_shared_passage_layout(self):
        """Variant MCQ with a fixed passage above the question list."""
        if not self.has_shared_passage or not self.is_variant_quiz:
            return False
        return bool(strip_tags(self.shared_passage or '').strip())

    @property
    def shared_audio_file_url(self):
        if not self.shared_audio_file:
            return ''
        try:
            return self.shared_audio_file.url
        except ValueError:
            return ''

    @property
    def uses_per_question_text_responses(self):
        """Free-text answer per task (writing / multi-part manual quizzes)."""
        if self.is_reading or self.is_math:
            return False
        if self.is_essay:
            return True
        if self.is_listening:
            return True
        if self.is_speaking:
            return False
        if not self.is_manual_grading:
            return False
        category = getattr(self, 'category', None)
        category_name = (category.name if category else '').strip().lower()
        if 'writing' in category_name:
            return True
        return self.questions.count() > 1

    def score_max_value(self, *, question_count=None):
        """Variant/reading/listening: one point per question; essay/speaking: 0–10 scale."""
        if self.is_manual_grading:
            return self.MANUAL_REVIEW_MAX_SCORE
        if question_count is None:
            if self.is_reading or self.is_math:
                from portals.utils.quiz_reading import get_reading_questions_for_quiz

                question_count = len(get_reading_questions_for_quiz(self))
            elif self.is_listening:
                from portals.utils.quiz_listening import get_listening_questions_for_quiz

                question_count = len(get_listening_questions_for_quiz(self))
            else:
                question_count = self.questions.count()
        return question_count

    @property
    def grading_mode(self):
        if self.is_listening:
            return 'listening'
        if self.is_essay:
            return 'essay'
        if self.is_speaking:
            return 'speaking'
        if self.is_math:
            return 'math'
        if self.is_reading:
            return 'reading'
        return 'variant'

    def get_grading_mode_label(self):
        if self.is_sat and self.sat_section:
            for value, label in self.SatSection.choices:
                if value == self.sat_section:
                    return str(label)
        labels = {
            'listening': 'Listening',
            'essay': _('Writing'),
            'speaking': 'Speaking',
            'reading': 'Reading',
            'math': _('Math'),
            'variant': 'Multiple choice',
        }
        return str(labels.get(self.grading_mode, self.grading_mode or ''))

    def apply_sat_section_format(self):
        """Sync format flags from sat_section when SAT is enabled."""
        self.is_listening = False
        self.is_speaking = False
        self.is_essay = False
        self.is_math = False
        self.is_reading = False
        if self.sat_section == self.SatSection.READING:
            self.is_reading = True

    @property
    def time_limit_seconds(self):
        if self.is_time_limited and self.time_limit_minutes:
            return int(self.time_limit_minutes) * 60
        return 0

    def get_course_type_codes(self):
        if not self.category_id:
            return []
        from portals.utils.quiz_category_services import quiz_category_portal_codes

        category = getattr(self, 'category', None)
        if category is None:
            category = QuizCategory.objects.filter(pk=self.category_id).prefetch_related('services').first()
        return quiz_category_portal_codes(category)

    def get_course_type_labels(self):
        from portals.utils.portal_services import get_course_type_label_map

        labels = get_course_type_label_map()
        code = self.service_code
        return [labels.get(code, code)] if code else []

    def clean(self):
        super().clean()

        format_flags = [
            self.is_listening,
            self.is_essay,
            self.is_speaking,
            self.is_reading,
            self.is_math,
        ]
        if sum(1 for flag in format_flags if flag) > 1:
            raise ValidationError(
                _('Only one quiz format can be enabled (Listening, Essay, Speaking, Reading, or Math).'),
            )

        if self.is_math and not self.is_sat:
            raise ValidationError({
                'is_math': _('Math format is only available when SAT is enabled.'),
            })

        if self.is_ielts and self.is_sat:
            raise ValidationError(_('Select only one mock test program: IELTS or SAT.'))

        if self.is_sat:
            if not self.sat_section:
                raise ValidationError({
                    'sat_section': _('Select a SAT section type (Reading, Writing, Algebra, or Geometry & Data).'),
                })
            if self.sat_section not in dict(self.SatSection.choices):
                raise ValidationError({'sat_section': _('Invalid SAT section type.')})
            self.apply_sat_section_format()
        else:
            self.sat_section = ''
            self.is_math = False

        if (
            self.is_listening
            or self.is_essay
            or self.is_speaking
            or self.is_reading
            or self.is_math
        ):
            self.has_shared_passage = False
        elif self.has_shared_passage:
            if not strip_tags(self.shared_passage or '').strip():
                raise ValidationError({
                    'shared_passage': _('Enter the shared passage text, or turn off shared passage layout.'),
                })
            if self.shared_audio_file and (self.shared_youtube_url or '').strip():
                raise ValidationError(
                    _('Choose either a shared audio file or a YouTube URL, not both.'),
                )
            if (self.shared_youtube_url or '').strip():
                from portals.utils.lesson_media import extract_youtube_video_id

                if not extract_youtube_video_id(self.shared_youtube_url):
                    raise ValidationError({
                        'shared_youtube_url': _('Enter a valid YouTube video URL.'),
                    })

        if self.is_time_limited:
            if not self.time_limit_minutes or self.time_limit_minutes < 1:
                raise ValidationError(
                    {'time_limit_minutes': _('Enter the time limit in minutes (at least 1).')},
                )
        elif self.time_limit_minutes:
            raise ValidationError(
                {'time_limit_minutes': _('Clear the time limit or enable time limited.')},
            )


class QuizQuestion(models.Model):
    class PromptType(models.TextChoices):
        TEXT = 'text', _('Text')
        IMAGE = 'image', _('Image')
        VIDEO = 'video', _('Video')
        AUDIO = 'audio', _('Audio')

    class QuestionType(models.TextChoices):
        MCQ = 'mcq', _('Multiple Choice')
        SPR = 'spr', _('Student-Produced Response')

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('Quiz'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
    )
    prompt_type = models.CharField(
        max_length=16,
        choices=PromptType.choices,
        default=PromptType.TEXT,
        verbose_name=_('Question type'),
    )
    question_type = models.CharField(
        max_length=10,
        choices=QuestionType.choices,
        default=QuestionType.MCQ,
        verbose_name=_('Answer type'),
        help_text=_('MCQ: Multiple choice with options. SPR: Student-Produced Response (typed answer).'),
    )
    is_dropdown = models.BooleanField(
        default=False,
        verbose_name=_('Dropdown answers'),
        help_text=_(
            'Show answer choices in a dropdown menu instead of a list. '
            'Use this when there are too many options for radio buttons.'
        ),
    )
    question = models.TextField(
        blank=True,
        verbose_name=_('Question text'),
        help_text=_('Written question or caption shown with image / video / audio.'),
    )
    media_file = models.FileField(
        upload_to='portals/quiz/media/',
        blank=True,
        null=True,
        verbose_name=_('Media file'),
        help_text=_('Upload image, video, or audio when the question type is not text.'),
    )
    media_url = models.URLField(
        blank=True,
        verbose_name=_('Media URL'),
        help_text=_('Optional external link (e.g. YouTube) instead of an uploaded file.'),
    )
    answer_options = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Answer options'),
        help_text=_('List of answer choices shown to the student. Not used for manual-review quizzes.'),
    )
    correct_option_index = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Correct option index'),
    )
    correct_answer = models.TextField(
        blank=True,
        verbose_name=_('Correct answer'),
    )
    spr_correct_answers = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('SPR correct answers'),
        help_text=_(
            'One or more accepted answers for SPR questions '
            '(e.g. ["7/2", "3.5"] or ["y = -x + 19"]).'
        ),
    )
    spr_max_length = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('SPR max length'),
        help_text=_(
            'Optional character limit for the student input. '
            'Leave blank for equations or free-text answers.'
        ),
    )
    source_key = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_('Source key'),
        help_text=_('Stable key for upsert when reloading JSON resources.'),
    )

    class Meta:
        verbose_name = _('Quiz question')
        verbose_name_plural = _('Quiz questions')
        ordering = ('order', 'id')
        constraints = [
            models.UniqueConstraint(
                fields=('quiz', 'source_key'),
                condition=~models.Q(source_key=''),
                name='portals_quiz_question_source_key_uniq',
            ),
        ]

    def __str__(self):
        if self.question:
            return self.question[:80]
        return str(_('Question %(pk)s') % {'pk': self.pk or '—'})

    @property
    def is_answerable(self):
        if (self.question or '').strip():
            return True
        if self.media_file:
            return True
        return bool((self.media_url or '').strip())

    @property
    def requires_student_response(self):
        """Audio bloku özü cavab tələb etmir — yalnız ondan sonrakı suallar cavab tələb edir."""
        return self.prompt_type != self.PromptType.AUDIO

    def clean(self):
        super().clean()
        quiz = self.quiz
        manual = quiz and quiz.is_manual_grading

        if manual:
            if self.prompt_type == self.PromptType.TEXT:
                if not (self.question or '').strip():
                    raise ValidationError(_('Enter the question text or task prompt.'))
            elif not self.media_file and not (self.media_url or '').strip():
                raise ValidationError(
                    _('Upload a media file or provide a media URL for this question type.'),
                )
            self.answer_options = []
            self.correct_answer = ''
            self.correct_option_index = 0
            self.spr_correct_answers = None
            self.spr_max_length = None
            self.is_dropdown = False
            return

        if self.question_type == self.QuestionType.SPR:
            self.answer_options = []
            self.correct_answer = ''
            self.correct_option_index = 0
            self.is_dropdown = False
            answers = [
                str(item).strip()
                for item in (self.spr_correct_answers or [])
                if str(item).strip()
            ]
            if not answers:
                raise ValidationError(
                    {'spr_correct_answers': _('SPR questions must have at least one correct answer.')},
                )
            self.spr_correct_answers = answers
        else:
            self.spr_correct_answers = None
            self.spr_max_length = None
            options = [str(item).strip() for item in (self.answer_options or []) if str(item).strip()]
            if len(options) < 2:
                raise ValidationError(
                    {'answer_options': _('Add at least two answer options.')},
                )

            correct = (self.correct_answer or '').strip()
            if correct and correct in options:
                self.correct_option_index = options.index(correct)
            elif options and 0 <= int(self.correct_option_index or 0) < len(options):
                # CKEditor often reformats HTML; keep the saved option index.
                self.correct_answer = options[int(self.correct_option_index)]
            elif correct:
                raise ValidationError(
                    {
                        'correct_answer': _(
                            'Correct answer must exactly match one of the options.',
                        ),
                    },
                )
            else:
                raise ValidationError(
                    {'correct_answer': _('Select which answer option is correct.')},
                )

        if self.prompt_type == self.PromptType.TEXT:
            if not (self.question or '').strip():
                raise ValidationError({'question': _('Enter the question text.')})
        elif not self.media_file and not (self.media_url or '').strip():
            raise ValidationError({
                'media_file': _('Upload a media file or provide a media URL for this question type.'),
            })

    def save(self, *args, **kwargs):
        quiz = None
        if self.quiz_id:
            quiz = Quiz.objects.filter(pk=self.quiz_id).only(
                'is_listening', 'is_essay', 'is_speaking',
            ).first()

        if quiz and quiz.is_manual_grading:
            self.answer_options = []
            self.correct_answer = ''
            self.correct_option_index = 0
            self.spr_correct_answers = None
            self.spr_max_length = None
            self.is_dropdown = False
            super().save(*args, **kwargs)
            return

        if self.question_type == self.QuestionType.SPR:
            self.answer_options = []
            self.correct_answer = ''
            self.correct_option_index = 0
            self.is_dropdown = False
            self.spr_correct_answers = [
                str(item).strip()
                for item in (self.spr_correct_answers or [])
                if str(item).strip()
            ] or None
            super().save(*args, **kwargs)
            return

        self.spr_correct_answers = None
        self.spr_max_length = None
        options = [str(item).strip() for item in (self.answer_options or []) if str(item).strip()]
        self.answer_options = options
        correct = (self.correct_answer or '').strip()
        if correct and correct in options:
            self.correct_answer = correct
            self.correct_option_index = options.index(correct)
        elif options and 0 <= self.correct_option_index < len(options):
            self.correct_answer = options[self.correct_option_index]
        else:
            self.correct_answer = ''
        super().save(*args, **kwargs)

    @property
    def uses_dropdown_answer(self):
        return bool(self.is_dropdown) and self.question_type != self.QuestionType.SPR

    @property
    def correct_option_label(self):
        options = self.answer_options or []
        index = self.correct_option_index
        if 0 <= index < len(options):
            return options[index]
        return self.correct_answer


class QuizResult(models.Model):
    """
    Student attempt for a quiz (named QuizResult to avoid clashing with projects.UserResult).
    """

    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='quiz_results',
        null=True,
        blank=True,
        verbose_name=_('Student'),
    )
    customer = models.ForeignKey(
        'CustomerProfile',
        on_delete=models.CASCADE,
        related_name='quiz_results',
        null=True,
        blank=True,
        verbose_name=_('Customer'),
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name=_('Quiz'),
    )
    given_answers = models.JSONField(
        default=dict,
        verbose_name=_('Given answers'),
        help_text=_('Map of question id → selected answer (variant quizzes) or free text.'),
    )
    student_submission = models.TextField(
        blank=True,
        verbose_name=_('Student submission'),
        help_text=_('Essay / listening / speaking response from the student.'),
    )
    total_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Total score'),
        help_text=_('Manual-review quizzes: score from 0 to 10. Variant quizzes: auto-calculated.'),
    )
    class CompletionTrigger(models.TextChoices):
        MANUAL = 'manual', _('Submitted by student')
        TIME_LIMIT = 'time_limit', _('Auto-submitted when time ran out')
        AUTO_LEAVE = 'auto_leave', _('Auto-submitted when student left')

    duration_sec = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Duration (seconds)'),
    )
    completion_trigger = models.CharField(
        max_length=20,
        choices=CompletionTrigger.choices,
        default=CompletionTrigger.MANUAL,
        verbose_name=_('Completion trigger'),
    )
    teacher_feedback = models.TextField(
        blank=True,
        verbose_name=_('Teacher feedback'),
        help_text=_('Corrections, reply, and comments from the teacher.'),
    )
    teacher_correct_answers = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Teacher correct answers'),
        help_text=_('Reading review: map of question id → teacher-entered correct answer.'),
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Reviewed at'),
    )
    completed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Completed at'),
    )
    ielts_mock_attempt = models.ForeignKey(
        'IeltsMockTestAttempt',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='section_results',
        verbose_name=_('IELTS mock test attempt'),
        help_text=_('Set when this result belongs to a mock test section (not a standalone quiz).'),
    )

    class Meta:
        verbose_name = _('Quiz result')
        verbose_name_plural = _('Quiz results')
        ordering = ('-completed_at', 'id')
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(student__isnull=False, customer__isnull=True)
                    | models.Q(student__isnull=True, customer__isnull=False)
                ),
                name='portals_quiz_result_student_xor_customer',
            ),
        ]

    @property
    def is_pending_review(self):
        if not self.quiz_id:
            return False
        quiz = getattr(self, 'quiz', None)
        if quiz is None:
            quiz = Quiz.objects.filter(pk=self.quiz_id).first()
        if not quiz or not quiz.requires_teacher_review:
            return False
        return self.reviewed_at is None

    def __str__(self):
        score = self.total_score if self.total_score is not None else '—'
        owner = self.student or self.customer
        return f'{owner} — {self.quiz} ({score})'


class QuizAssignment(models.Model):
    """Per-student quiz access — teachers activate or deactivate individual quizzes."""

    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='quiz_assignments',
        verbose_name=_('Student'),
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='student_assignments',
        verbose_name=_('Quiz'),
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_('Active'),
        help_text=_('When enabled, the student can see and take this quiz.'),
    )
    assigned_by = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quiz_assignments_created',
        verbose_name=_('Assigned by'),
    )
    assigned_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )

    class Meta:
        verbose_name = _('Quiz assignment')
        verbose_name_plural = _('Quiz assignments')
        constraints = [
            models.UniqueConstraint(
                fields=('student', 'quiz'),
                name='portals_quiz_assignment_uniq',
            ),
        ]
        ordering = ('-assigned_at', 'id')

    def __str__(self):
        state = _('active') if self.is_active else _('inactive')
        return f'{self.student} — {self.quiz} ({state})'


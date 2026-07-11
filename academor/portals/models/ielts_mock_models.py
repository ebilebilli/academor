from django.db import models
from django.utils.translation import gettext_lazy as _


class IeltsMockTestAttempt(models.Model):
    """Full mock test session chaining section quizzes for one exam program."""

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', _('In progress')
        COMPLETED = 'completed', _('Completed')
        ABANDONED = 'abandoned', _('Abandoned')

    class Section(models.TextChoices):
        LISTENING = 'listening', _('Listening')
        READING = 'reading', _('Reading')
        WRITING = 'writing', _('Writing')
        SPEAKING = 'speaking', _('Speaking')
        READING_WRITING = 'reading_writing', _('Reading and Writing')
        MATH = 'math', _('Math')

    SECTION_ORDER = (
        Section.LISTENING,
        Section.READING,
        Section.WRITING,
        Section.SPEAKING,
    )

    class ExamProgram(models.TextChoices):
        IELTS = 'ielts', _('IELTS')
        SAT = 'sat', _('SAT')

    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='ielts_mock_attempts',
        null=True,
        blank=True,
        verbose_name=_('Student'),
    )
    customer = models.ForeignKey(
        'CustomerProfile',
        on_delete=models.CASCADE,
        related_name='ielts_mock_attempts',
        null=True,
        blank=True,
        verbose_name=_('Customer'),
    )
    exam_program = models.CharField(
        max_length=16,
        choices=ExamProgram.choices,
        default=ExamProgram.IELTS,
        db_index=True,
        verbose_name=_('Exam program'),
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        db_index=True,
        verbose_name=_('Status'),
    )
    current_section = models.CharField(
        max_length=20,
        choices=Section.choices,
        default=Section.LISTENING,
        verbose_name=_('Current section'),
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Started at'))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Completed at'))
    credit_consumed = models.BooleanField(
        default=False,
        verbose_name=_('Credit consumed'),
        help_text=_('Customer mock credit is deducted when the first quiz section starts.'),
    )

    listening_quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.PROTECT,
        related_name='mock_listening_attempts',
        null=True,
        blank=True,
        verbose_name=_('Listening quiz'),
    )
    reading_quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.PROTECT,
        related_name='mock_reading_attempts',
        verbose_name=_('Reading quiz'),
    )
    writing_quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.PROTECT,
        related_name='mock_writing_attempts',
        null=True,
        blank=True,
        verbose_name=_('Writing quiz'),
    )
    speaking_quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.PROTECT,
        related_name='mock_speaking_attempts',
        null=True,
        blank=True,
        verbose_name=_('Speaking quiz'),
    )
    math_quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.PROTECT,
        related_name='mock_math_attempts',
        null=True,
        blank=True,
        verbose_name=_('Math quiz'),
    )

    listening_result = models.ForeignKey(
        'QuizResult',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mock_listening_for',
        verbose_name=_('Listening result'),
    )
    reading_result = models.ForeignKey(
        'QuizResult',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mock_reading_for',
        verbose_name=_('Reading result'),
    )
    writing_result = models.ForeignKey(
        'QuizResult',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mock_writing_for',
        verbose_name=_('Writing result'),
    )
    speaking_result = models.ForeignKey(
        'QuizResult',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mock_speaking_for',
        verbose_name=_('Speaking result'),
    )
    math_result = models.ForeignKey(
        'QuizResult',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mock_math_for',
        verbose_name=_('Math result'),
    )

    class Meta:
        verbose_name = _('Mock test attempt')
        verbose_name_plural = _('Mock test attempts')
        ordering = ('-started_at', '-id')
        indexes = [
            models.Index(fields=['student', 'status', '-started_at']),
            models.Index(fields=['customer', 'status', '-started_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(student__isnull=False, customer__isnull=True)
                    | models.Q(student__isnull=True, customer__isnull=False)
                ),
                name='portals_mock_attempt_student_xor_customer',
            ),
        ]

    def __str__(self):
        return f'{self.student_id} — {self.get_status_display()} ({self.pk})'

    def program_section_order(self) -> tuple[str, ...]:
        from portals.utils.mock_programs import get_section_order

        return get_section_order(self.exam_program)

    def quiz_for_section(self, section: str):
        from portals.utils.mock_programs import get_section_spec

        spec = get_section_spec(self.exam_program, section)
        if not spec:
            return None
        return getattr(self, spec.quiz_field, None)

    def result_for_section(self, section: str):
        from portals.utils.mock_programs import get_section_spec

        spec = get_section_spec(self.exam_program, section)
        if not spec:
            return None
        return getattr(self, spec.result_field, None)

    def section_index(self, section: str | None = None) -> int:
        from portals.utils.mock_programs import section_index_for_program

        section = section or self.current_section
        return section_index_for_program(self.exam_program, section)


class StudentMockAccess(models.Model):
    """Teacher-controlled mock test availability for one student and exam program."""

    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='mock_access_entries',
        verbose_name=_('Student'),
    )
    exam_program = models.CharField(
        max_length=16,
        verbose_name=_('Exam program'),
        help_text=_('Mock exam program code, e.g. ielts or sat.'),
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_('Active'),
        help_text=_('When enabled, the student can start this mock test program.'),
    )
    assigned_by = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mock_access_granted',
        verbose_name=_('Assigned by'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )

    class Meta:
        verbose_name = _('Student mock access')
        verbose_name_plural = _('Student mock access')
        ordering = ('-updated_at', 'id')
        constraints = [
            models.UniqueConstraint(
                fields=('student', 'exam_program'),
                name='portals_student_mock_access_program_uniq',
            ),
        ]

    def __str__(self):
        state = _('active') if self.is_active else _('inactive')
        return f'{self.student} — {self.exam_program} mock ({state})'


MockTestAttempt = IeltsMockTestAttempt

from django.db import models
from django.utils.translation import gettext_lazy as _


class IeltsMockTestAttempt(models.Model):
    """Full IELTS mock test session chaining four section quizzes."""

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', _('In progress')
        COMPLETED = 'completed', _('Completed')
        ABANDONED = 'abandoned', _('Abandoned')

    class Section(models.TextChoices):
        LISTENING = 'listening', _('Listening')
        READING = 'reading', _('Reading')
        WRITING = 'writing', _('Writing')
        SPEAKING = 'speaking', _('Speaking')

    SECTION_ORDER = (
        Section.LISTENING,
        Section.READING,
        Section.WRITING,
        Section.SPEAKING,
    )

    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='ielts_mock_attempts',
        verbose_name=_('Student'),
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        db_index=True,
        verbose_name=_('Status'),
    )
    current_section = models.CharField(
        max_length=16,
        choices=Section.choices,
        default=Section.LISTENING,
        verbose_name=_('Current section'),
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Started at'))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Completed at'))

    listening_quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.PROTECT,
        related_name='mock_listening_attempts',
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
        verbose_name=_('Writing quiz'),
    )
    speaking_quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.PROTECT,
        related_name='mock_speaking_attempts',
        verbose_name=_('Speaking quiz'),
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

    class Meta:
        verbose_name = _('IELTS mock test attempt')
        verbose_name_plural = _('IELTS mock test attempts')
        ordering = ('-started_at', '-id')
        indexes = [
            models.Index(fields=['student', 'status', '-started_at']),
        ]

    def __str__(self):
        return f'{self.student_id} — {self.get_status_display()} ({self.pk})'

    def quiz_for_section(self, section: str):
        mapping = {
            self.Section.LISTENING: self.listening_quiz,
            self.Section.READING: self.reading_quiz,
            self.Section.WRITING: self.writing_quiz,
            self.Section.SPEAKING: self.speaking_quiz,
        }
        return mapping.get(section)

    def result_for_section(self, section: str):
        mapping = {
            self.Section.LISTENING: self.listening_result,
            self.Section.READING: self.reading_result,
            self.Section.WRITING: self.writing_result,
            self.Section.SPEAKING: self.speaking_result,
        }
        return mapping.get(section)

    def section_index(self, section: str | None = None) -> int:
        section = section or self.current_section
        try:
            return self.SECTION_ORDER.index(section) + 1
        except ValueError:
            return 0

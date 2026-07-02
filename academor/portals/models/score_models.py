from django.db import models
from django.utils.translation import gettext_lazy as _


class Score(models.Model):
    class ScoreType(models.TextChoices):
        HOMEWORK = 'homework', _('Homework')
        EXAM = 'exam', _('Exam')
        QUIZ = 'quiz', _('Quiz')

    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='scores',
        verbose_name=_('Student'),
    )
    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scores',
        verbose_name=_('Lesson'),
        help_text=_('Optional — homework and exams may not map to a single lesson.'),
    )
    score_type = models.CharField(
        max_length=16,
        choices=ScoreType.choices,
        db_index=True,
        verbose_name=_('Score type'),
    )
    value = models.FloatField(
        verbose_name=_('Value'),
    )
    max_value = models.FloatField(
        verbose_name=_('Max value'),
    )
    date = models.DateTimeField(
        verbose_name=_('Date'),
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_('Comment'),
    )

    class Meta:
        verbose_name = _('Score')
        verbose_name_plural = _('Scores')
        ordering = ('-date', '-id')

    def __str__(self):
        return f'{self.student} — {self.get_score_type_display()}: {self.value}/{self.max_value}'

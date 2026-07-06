from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

WEEKLY_SCORE_MAX = 10


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
        validators=[MinValueValidator(0)],
    )
    max_value = models.FloatField(
        verbose_name=_('Max value'),
        validators=[MinValueValidator(0)],
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

    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()
        if self.max_value is not None and self.max_value <= 0:
            raise ValidationError({'max_value': _('Max value must be greater than zero.')})
        if (
            self.value is not None
            and self.max_value is not None
            and self.value > self.max_value
        ):
            raise ValidationError({'value': _('Score cannot exceed max value.')})

    def __str__(self):
        return f'{self.student} — {self.get_score_type_display()}: {self.value}/{self.max_value}'


class WeeklyStudentScore(models.Model):
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='weekly_scores',
        verbose_name=_('Student'),
    )
    teacher = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.CASCADE,
        related_name='weekly_scores_given',
        verbose_name=_('Teacher'),
    )
    week_start = models.DateField(
        db_index=True,
        verbose_name=_('Week start'),
        help_text=_('Monday of the scored week.'),
    )
    score = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(WEEKLY_SCORE_MAX),
        ],
        verbose_name=_('Score'),
        help_text=_('Score out of 10 for the week.'),
    )
    comment = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_('Comment'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at'),
    )

    class Meta:
        verbose_name = _('Weekly student score')
        verbose_name_plural = _('Weekly student scores')
        ordering = ('-week_start', '-updated_at', '-id')
        constraints = [
            models.UniqueConstraint(
                fields=('student', 'teacher', 'week_start'),
                name='portals_weekly_score_unique_student_teacher_week',
            ),
        ]

    def __str__(self):
        return f'{self.student} — {self.week_start}: {self.score}/{WEEKLY_SCORE_MAX}'

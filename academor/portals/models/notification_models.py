from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class QuizResultReview(models.Model):
    """Teacher grading record for a manual-review quiz submission."""

    result = models.ForeignKey(
        'QuizResult',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Quiz result'),
    )
    reviewer = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.PROTECT,
        related_name='quiz_result_reviews',
        verbose_name=_('Reviewer'),
    )
    score = models.FloatField(verbose_name=_('Score'))
    feedback = models.TextField(
        blank=True,
        verbose_name=_('Feedback and corrections'),
    )
    reviewed_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Reviewed at'))

    class Meta:
        verbose_name = _('Quiz result review')
        verbose_name_plural = _('Quiz result reviews')
        ordering = ('-reviewed_at', 'id')

    def __str__(self):
        return f'{self.reviewer} → {self.result_id} ({self.score})'


class PortalNotification(models.Model):
    """Portal alerts for quiz submissions and published scores."""

    class Kind(models.TextChoices):
        SUBMISSION_PENDING = 'submission_pending', _('Submission awaiting review')
        RESULT_PUBLISHED = 'result_published', _('Result published')

    teacher = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Teacher'),
    )
    parent = models.ForeignKey(
        'ParentProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Parent'),
    )
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Student'),
    )
    quiz_result = models.ForeignKey(
        'QuizResult',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Quiz result'),
    )
    kind = models.CharField(
        max_length=32,
        choices=Kind.choices,
        default=Kind.RESULT_PUBLISHED,
        verbose_name=_('Type'),
    )
    is_read = models.BooleanField(default=False, verbose_name=_('Read'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Portal notification')
        verbose_name_plural = _('Portal notifications')
        ordering = ('-created_at', '-id')
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(teacher__isnull=False, parent__isnull=True, student__isnull=True)
                    | Q(teacher__isnull=True, parent__isnull=False, student__isnull=True)
                    | Q(teacher__isnull=True, parent__isnull=True, student__isnull=False)
                ),
                name='portals_notification_single_recipient',
            ),
            models.UniqueConstraint(
                fields=('teacher', 'quiz_result', 'kind'),
                condition=Q(teacher__isnull=False),
                name='portals_notification_teacher_result_kind_unique',
            ),
            models.UniqueConstraint(
                fields=('parent', 'quiz_result'),
                condition=Q(parent__isnull=False),
                name='portals_notification_parent_result_unique',
            ),
            models.UniqueConstraint(
                fields=('student', 'quiz_result'),
                condition=Q(student__isnull=False),
                name='portals_notification_student_result_unique',
            ),
        ]
        indexes = [
            models.Index(fields=['teacher', 'is_read', '-created_at']),
            models.Index(fields=['parent', 'is_read', '-created_at']),
            models.Index(fields=['student', 'is_read', '-created_at']),
        ]

    def __str__(self):
        recipient = self.teacher or self.parent or self.student
        return f'{recipient} — {self.get_kind_display()} ({self.quiz_result_id})'

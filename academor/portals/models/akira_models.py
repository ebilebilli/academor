"""AKIRA — Academor Knowledge & Intelligent Research Assistant.

Course-neutral storage: one report per attempt (portal quiz or public test), a usage
log for the monthly budget, approved explanations per question and answer, and a
knowledge base of Academor's own materials that AKIRA reads before it writes.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AkiraReport(models.Model):
    class Kind(models.TextChoices):
        QUIZ = 'quiz', _('Portal quiz')
        PUBLIC_TEST = 'public_test', _('Public test')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        READY = 'ready', _('Ready')
        FAILED = 'failed', _('Failed')
        SKIPPED = 'skipped', _('Skipped (limit or switched off)')

    kind = models.CharField(max_length=20, choices=Kind.choices, verbose_name=_('Kind'))
    course_code = models.CharField(max_length=40, db_index=True, verbose_name=_('Course'))
    quiz_result = models.OneToOneField(
        'portals.QuizResult',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='akira_report',
        verbose_name=_('Quiz result'),
    )
    user_result = models.OneToOneField(
        'projects.UserResult',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='akira_report',
        verbose_name=_('Public test result'),
    )
    student = models.ForeignKey(
        'portals.StudentProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='akira_reports',
        verbose_name=_('Student'),
    )
    customer = models.ForeignKey(
        'portals.CustomerProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='akira_reports',
        verbose_name=_('Customer'),
    )
    facts = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Facts'),
        help_text=_('Numbers computed by the system. AKIRA only puts these into words.'),
    )
    comment = models.TextField(blank=True, verbose_name=_('AKIRA comment'))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name=_('Status'),
    )
    model_name = models.CharField(max_length=60, blank=True, verbose_name=_('Model'))
    error = models.CharField(max_length=255, blank=True, verbose_name=_('Error'))
    attempts = models.PositiveSmallIntegerField(default=0, verbose_name=_('Attempts'))
    helpful = models.BooleanField(null=True, blank=True, verbose_name=_('Marked helpful'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('AKIRA report')
        verbose_name_plural = _('AKIRA reports')
        ordering = ('-created_at',)

    def __str__(self):
        return f'AKIRA {self.get_kind_display()} #{self.pk} ({self.course_code})'


class AkiraUsage(models.Model):
    """One call to the AI. The monthly budget is the sum of ``cost_usd`` this month."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('Created at'))
    purpose = models.CharField(max_length=40, verbose_name=_('Purpose'))
    model_name = models.CharField(max_length=60, verbose_name=_('Model'))
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    cache_read_tokens = models.PositiveIntegerField(default=0)
    cache_write_tokens = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=5, default=0, verbose_name=_('Cost (USD)'))
    ok = models.BooleanField(default=True, verbose_name=_('Succeeded'))
    report = models.ForeignKey(
        AkiraReport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usage',
    )

    class Meta:
        verbose_name = _('AKIRA usage')
        verbose_name_plural = _('AKIRA usage')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.purpose} · ${self.cost_usd}'


class AkiraExplanation(models.Model):
    """Why one answer to one question is right or wrong. Shown to students only once approved."""

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Waiting for teacher review')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    question = models.ForeignKey(
        'portals.QuizQuestion',
        on_delete=models.CASCADE,
        related_name='akira_explanations',
        verbose_name=_('Question'),
    )
    answer_key = models.CharField(
        max_length=40,
        verbose_name=_('Answer'),
        help_text=_('Option index (0, 1, 2…), "blank", or "general" for the whole question.'),
    )
    text = models.TextField(verbose_name=_('Explanation'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_('Reviewed by'),
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Reviewed at'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('AKIRA explanation')
        verbose_name_plural = _('AKIRA explanations')
        constraints = [
            models.UniqueConstraint(fields=('question', 'answer_key'), name='portals_akira_explanation_uniq'),
        ]

    def __str__(self):
        return f'{self.question_id} · {self.answer_key}'


class AkiraMaterial(models.Model):
    """Academor's own teaching material. AKIRA reads the matching pieces before it writes.

    Upload only material you own or have the right to use.
    """

    course_code = models.CharField(
        max_length=40,
        db_index=True,
        verbose_name=_('Course'),
        help_text=_('Course code, e.g. sat-math, sat-verbal, ielts, general_english, fmva, dipifr.'),
    )
    domain = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name=_('Topic area'),
        help_text=_('Optional. When set, the material is used for this topic area only (e.g. Algebra).'),
    )
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Content'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('AKIRA material')
        verbose_name_plural = _('AKIRA materials')
        ordering = ('course_code', 'domain', 'title')

    def __str__(self):
        return self.title

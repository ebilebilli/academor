from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


class ReadingQuestionType(models.TextChoices):
    MCQ = 'mcq', _('Multiple choice')
    TFNG = 'tfng', _('True / False / Not Given')
    YNNG = 'ynng', _('Yes / No / Not Given')
    SENTENCE_COMPLETION = 'sentence_completion', _('Sentence completion')
    SUMMARY_COMPLETION = 'summary_completion', _('Summary completion')
    NOTE_COMPLETION = 'note_completion', _('Note completion')
    TABLE_COMPLETION = 'table_completion', _('Table completion')
    FLOWCHART_COMPLETION = 'flowchart_completion', _('Flow-chart completion')
    DIAGRAM_LABEL = 'diagram_label', _('Diagram label completion')
    SHORT_ANSWER = 'short_answer', _('Short answer')
    MATCHING_HEADINGS = 'matching_headings', _('Matching headings')
    MATCHING_INFO = 'matching_info', _('Matching information')
    MATCHING_FEATURES = 'matching_features', _('Matching features')
    MATCHING_SENTENCE_ENDINGS = 'matching_sentence_endings', _('Matching sentence endings')


MATCHING_QUESTION_TYPES = frozenset({
    ReadingQuestionType.MATCHING_HEADINGS,
    ReadingQuestionType.MATCHING_INFO,
    ReadingQuestionType.MATCHING_FEATURES,
    ReadingQuestionType.MATCHING_SENTENCE_ENDINGS,
})

CHOICE_QUESTION_TYPES = frozenset({
    ReadingQuestionType.MCQ,
    ReadingQuestionType.TFNG,
    ReadingQuestionType.YNNG,
    *MATCHING_QUESTION_TYPES,
})

TEXT_QUESTION_TYPES = frozenset({
    ReadingQuestionType.SENTENCE_COMPLETION,
    ReadingQuestionType.SUMMARY_COMPLETION,
    ReadingQuestionType.NOTE_COMPLETION,
    ReadingQuestionType.TABLE_COMPLETION,
    ReadingQuestionType.FLOWCHART_COMPLETION,
    ReadingQuestionType.DIAGRAM_LABEL,
    ReadingQuestionType.SHORT_ANSWER,
})

TFNG_OPTIONS = ['True', 'False', 'Not Given']
YNNG_OPTIONS = ['Yes', 'No', 'Not Given']


def resolve_reading_question_options(question: 'ReadingQuestion') -> list[str]:
    if question.question_type == ReadingQuestionType.TFNG:
        return list(TFNG_OPTIONS)
    if question.question_type == ReadingQuestionType.YNNG:
        return list(YNNG_OPTIONS)
    if question.group_id and question.group:
        pool = question.group.pool_options
        if len(pool) >= 2:
            return pool
    if question.question_type == ReadingQuestionType.MCQ:
        return [
            str(item).strip()
            for item in (question.answer_options or [])
            if str(item).strip()
        ]
    return [
        str(item).strip()
        for item in (question.answer_options or [])
        if str(item).strip()
    ]


class ReadingPassage(models.Model):
    """Reading passage for an IELTS-style reading quiz."""

    quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.CASCADE,
        related_name='reading_passages',
        verbose_name=_('Quiz'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Title'),
        help_text=_('Short label, e.g. Passage 1.'),
    )
    instructions = RichTextField(
        blank=True,
        verbose_name=_('Instructions'),
        help_text=_('Task instructions shown above the passage.'),
    )
    body = RichTextField(
        verbose_name=_('Passage text'),
        help_text=_('The reading passage shown to the student.'),
    )

    class Meta:
        verbose_name = _('Reading passage')
        verbose_name_plural = _('Reading passages')
        ordering = ('order', 'id')

    def __str__(self):
        label = (self.title or strip_tags(self.body or '') or '').strip()
        if label:
            return label[:80]
        return str(_('Reading passage %(pk)s') % {'pk': self.pk or '—'})

    def clean(self):
        super().clean()
        if not strip_tags(self.body or '').strip():
            raise ValidationError({'body': _('Enter the passage text.')})
        if self.quiz_id and not (self.quiz.is_reading or self.quiz.is_math):
            raise ValidationError({'quiz': _('Select a reading or math quiz.')})


class ReadingQuestionGroup(models.Model):
    """Shared option pool for matching-style reading tasks."""

    passage = models.ForeignKey(
        ReadingPassage,
        on_delete=models.CASCADE,
        related_name='question_groups',
        verbose_name=_('Passage'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Title'),
    )
    instructions = RichTextField(
        blank=True,
        verbose_name=_('Instructions'),
    )
    question_type = models.CharField(
        max_length=32,
        choices=ReadingQuestionType.choices,
        verbose_name=_('Question type'),
    )
    option_pool = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Option pool'),
        help_text=_('Shared choices for matching tasks, e.g. headings or endings.'),
    )

    class Meta:
        verbose_name = _('Reading question group')
        verbose_name_plural = _('Reading question groups')
        ordering = ('order', 'id')

    def __str__(self):
        label = (self.title or self.get_question_type_display() or '').strip()
        if label:
            return label[:80]
        return str(_('Question group %(pk)s') % {'pk': self.pk or '—'})

    @property
    def pool_options(self) -> list[str]:
        return [str(item).strip() for item in (self.option_pool or []) if str(item).strip()]

    def clean(self):
        super().clean()
        if self.question_type not in MATCHING_QUESTION_TYPES:
            raise ValidationError(
                {'question_type': _('Question group type must be a matching task.')},
            )
        if len(self.pool_options) < 2:
            raise ValidationError(
                {'option_pool': _('Add at least two options to the pool.')},
            )


class ReadingQuestion(models.Model):
    """Single numbered reading task (gap, choice, or matching item)."""

    passage = models.ForeignKey(
        ReadingPassage,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('Passage'),
    )
    group = models.ForeignKey(
        ReadingQuestionGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions',
        verbose_name=_('Question group'),
        help_text=_('Optional shared option pool for matching tasks.'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
    )
    question_type = models.CharField(
        max_length=32,
        choices=ReadingQuestionType.choices,
        default=ReadingQuestionType.MCQ,
        verbose_name=_('Question type'),
    )
    question = RichTextField(
        blank=True,
        verbose_name=_('Question'),
        help_text=_(
            'Prompt, table, flow-chart, or diagram context. '
            'Leave blank for a numbered answer line only when appropriate.',
        ),
    )
    answer_options = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Answer options'),
        help_text=_('Required for multiple choice. Leave empty for fixed or group options.'),
    )
    correct_option_index = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Correct option index'),
    )
    correct_answer = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Correct answer'),
        help_text=_('Exact text for gap-fill tasks or the matching option label.'),
    )
    question_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Question config'),
        help_text=_('Word limits, alternatives, paragraph refs, etc.'),
    )

    class Meta:
        verbose_name = _('Reading question')
        verbose_name_plural = _('Reading questions')
        ordering = ('order', 'id')

    def __str__(self):
        if self.question:
            return strip_tags(self.question)[:80]
        return str(_('Question %(order)s') % {'order': self.order or '—'})

    @property
    def is_choice_type(self) -> bool:
        return self.question_type in CHOICE_QUESTION_TYPES

    @property
    def is_text_type(self) -> bool:
        return self.question_type in TEXT_QUESTION_TYPES

    @property
    def variant_options(self) -> list[str]:
        return resolve_reading_question_options(self)

    @property
    def is_variant(self) -> bool:
        return len(self.variant_options) >= 2

    @property
    def is_answerable(self) -> bool:
        if self.is_choice_type:
            return True
        if self.is_text_type:
            return bool(strip_tags(self.question or '').strip()) or bool((self.correct_answer or '').strip())
        return bool(strip_tags(self.question or '').strip())

    def clean(self):
        super().clean()
        if self.group_id and self.group.passage_id != self.passage_id:
            raise ValidationError({'group': _('Question group must belong to the same passage.')})
        if self.group_id and self.question_type != self.group.question_type:
            raise ValidationError(
                {'question_type': _('Question type must match the selected group.')},
            )

        options = self.variant_options
        if self.is_choice_type:
            if len(options) < 2:
                raise ValidationError(
                    _('Add answer options, a matching group, or use a fixed choice type.'),
                )
            correct = (self.correct_answer or '').strip()
            if not correct:
                raise ValidationError({'correct_answer': _('Enter the correct answer.')})
            if correct not in options:
                raise ValidationError(
                    {'correct_answer': _('Correct answer must exactly match one of the options.')},
                )
            self.correct_option_index = options.index(correct)
            return

        if self.is_text_type:
            self.answer_options = []
            self.correct_option_index = 0
            correct = (self.correct_answer or '').strip()
            if not correct:
                raise ValidationError({'correct_answer': _('Enter the correct answer.')})
            return

        raise ValidationError({'question_type': _('Unsupported question type.')})

    def save(self, *args, **kwargs):
        if self.is_text_type:
            self.answer_options = []
            self.correct_option_index = 0
        elif self.is_choice_type:
            options = self.variant_options
            if len(options) >= 2:
                if self.question_type == ReadingQuestionType.MCQ:
                    self.answer_options = [
                        str(item).strip()
                        for item in (self.answer_options or [])
                        if str(item).strip()
                    ]
                correct = (self.correct_answer or '').strip()
                if correct in options:
                    self.correct_option_index = options.index(correct)
        super().save(*args, **kwargs)

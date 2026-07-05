from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


class SpeakingPartType(models.TextChoices):
    PART_1 = 'part_1', _('Part 1 — Introduction & interview')
    PART_2 = 'part_2', _('Part 2 — Individual long turn')
    PART_3 = 'part_3', _('Part 3 — Two-way discussion')


# Official IELTS speaking timing guidance (practice defaults).
IELTS_SPEAKING_PART_TIMING = {
    SpeakingPartType.PART_1: {'preparation_seconds': 0, 'answer_seconds': 30},
    SpeakingPartType.PART_2: {'preparation_seconds': 60, 'answer_seconds': 120},
    SpeakingPartType.PART_3: {'preparation_seconds': 0, 'answer_seconds': 90},
}

IELTS_SPEAKING_TOTAL_MINUTES_DEFAULT = 14


class SpeakingPart(models.Model):
    """IELTS speaking part (1, 2, or 3) for a speaking quiz."""

    quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.CASCADE,
        related_name='speaking_parts',
        verbose_name=_('Quiz'),
    )
    part_type = models.CharField(
        max_length=16,
        choices=SpeakingPartType.choices,
        verbose_name=_('Part'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Title'),
        help_text=_('Optional label shown to the student.'),
    )
    instructions = RichTextField(
        blank=True,
        verbose_name=_('Instructions'),
        help_text=_('Official-style task instructions for this part.'),
    )
    cue_card_topic = RichTextField(
        blank=True,
        verbose_name=_('Cue card topic'),
        help_text=_('Part 2 only — main topic line on the cue card.'),
    )
    cue_card_bullets = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Cue card bullet points'),
        help_text=_('Part 2 only — "You should say" bullet list.'),
    )
    preparation_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Preparation time (seconds)'),
        help_text=_('Leave blank to use the IELTS default for this part.'),
    )
    default_answer_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Default answer time (seconds)'),
        help_text=_('Per-question recording limit when a question has no override.'),
    )

    class Meta:
        verbose_name = _('Speaking part')
        verbose_name_plural = _('Speaking parts')
        ordering = ('order', 'id')

    def __str__(self):
        label = (self.title or self.get_part_type_display() or '').strip()
        return label[:80] if label else str(_('Speaking part %(pk)s') % {'pk': self.pk or '—'})

    @property
    def resolved_preparation_seconds(self) -> int:
        if self.preparation_seconds is not None:
            return self.preparation_seconds
        return IELTS_SPEAKING_PART_TIMING[self.part_type]['preparation_seconds']

    @property
    def resolved_default_answer_seconds(self) -> int:
        if self.default_answer_seconds is not None:
            return self.default_answer_seconds
        return IELTS_SPEAKING_PART_TIMING[self.part_type]['answer_seconds']

    def clean(self):
        super().clean()
        if self.quiz_id and not self.quiz.is_speaking:
            raise ValidationError({'quiz': _('Select a speaking quiz.')})
        if self.part_type == SpeakingPartType.PART_2:
            if not strip_tags(self.cue_card_topic or '').strip():
                raise ValidationError({'cue_card_topic': _('Enter the Part 2 cue card topic.')})
        bullets = [str(item).strip() for item in (self.cue_card_bullets or []) if str(item).strip()]
        self.cue_card_bullets = bullets


class SpeakingQuestion(models.Model):
    """Single speaking prompt within a part — student records one audio answer per question."""

    part = models.ForeignKey(
        SpeakingPart,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('Part'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
    )
    question = RichTextField(
        blank=True,
        verbose_name=_('Question'),
        help_text=_('Examiner question. Leave blank for Part 2 when the cue card is the prompt.'),
    )
    preparation_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Preparation time (seconds)'),
        help_text=_('Override part default. Part 2 uses this before the long-turn recording.'),
    )
    answer_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Answer time (seconds)'),
        help_text=_('Maximum recording length for this question.'),
    )

    class Meta:
        verbose_name = _('Speaking question')
        verbose_name_plural = _('Speaking questions')
        ordering = ('order', 'id')

    def __str__(self):
        text = strip_tags(self.question or '').strip()
        if text:
            return text[:80]
        part = getattr(self, 'part', None)
        if part and part.part_type == SpeakingPartType.PART_2:
            return str(_('Part 2 long turn'))
        return str(_('Question %(order)s') % {'order': self.order or '—'})

    @property
    def is_answerable(self) -> bool:
        if strip_tags(self.question or '').strip():
            return True
        part = getattr(self, 'part', None)
        if part and part.part_type == SpeakingPartType.PART_2:
            return bool(strip_tags(part.cue_card_topic or '').strip())
        return False

    @property
    def resolved_preparation_seconds(self) -> int:
        if self.preparation_seconds is not None:
            return self.preparation_seconds
        part = getattr(self, 'part', None)
        if part is not None:
            return part.resolved_preparation_seconds
        return 0

    @property
    def resolved_answer_seconds(self) -> int:
        if self.answer_seconds is not None:
            return self.answer_seconds
        part = getattr(self, 'part', None)
        if part is not None:
            return part.resolved_default_answer_seconds
        return IELTS_SPEAKING_PART_TIMING[SpeakingPartType.PART_1]['answer_seconds']


class SpeakingRecording(models.Model):
    """Student audio answer for one speaking question."""

    result = models.ForeignKey(
        'QuizResult',
        on_delete=models.CASCADE,
        related_name='speaking_recordings',
        verbose_name=_('Quiz result'),
    )
    question = models.ForeignKey(
        SpeakingQuestion,
        on_delete=models.CASCADE,
        related_name='recordings',
        verbose_name=_('Question'),
    )
    audio_file = models.FileField(
        upload_to='portals/speaking/recordings/%Y/%m/',
        verbose_name=_('Audio recording'),
    )
    duration_sec = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Duration (seconds)'),
    )

    class Meta:
        verbose_name = _('Speaking recording')
        verbose_name_plural = _('Speaking recordings')
        constraints = [
            models.UniqueConstraint(
                fields=('result', 'question'),
                name='portals_speaking_recording_uniq',
            ),
        ]
        ordering = ('question__part__order', 'question__order', 'id')

    def __str__(self):
        return str(_('Recording for question %(pk)s') % {'pk': self.question_id or '—'})

    @property
    def audio_url(self) -> str:
        if self.audio_file:
            try:
                return self.audio_file.url
            except ValueError:
                return ''
        return ''

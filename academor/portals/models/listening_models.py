from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


class ListeningQuestionType(models.TextChoices):
    MAP_LABELLING = 'map_labelling', _('Map labelling')
    PLAN_LABELLING = 'plan_labelling', _('Plan labelling')


LABEL_GROUP_QUESTION_TYPES = frozenset({
    ListeningQuestionType.MAP_LABELLING,
    ListeningQuestionType.PLAN_LABELLING,
})


class ListeningAudio(models.Model):
    """Listening clip for a listening quiz (IELTS-style audio section)."""

    quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.CASCADE,
        related_name='listening_audios',
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
        help_text=_('Short label, e.g. Section 1.'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Instructions or context shown with the audio.'),
    )
    audio_file = models.FileField(
        upload_to='portals/listening/audio/',
        blank=True,
        null=True,
        verbose_name=_('Audio file'),
    )
    audio_url = models.URLField(
        blank=True,
        verbose_name=_('Audio URL'),
        help_text=_('Optional external audio link instead of an uploaded file.'),
    )

    class Meta:
        verbose_name = _('Listening audio')
        verbose_name_plural = _('Listening audio clips')
        ordering = ('order', 'id')

    def __str__(self):
        label = (self.title or self.description or '').strip()
        if label:
            return label[:80]
        return str(_('Listening audio %(pk)s') % {'pk': self.pk or '—'})

    def clean(self):
        super().clean()
        if not self.audio_file and not (self.audio_url or '').strip():
            raise ValidationError(_('Upload an audio file or provide an audio URL.'))
        if self.quiz_id and not self.quiz.is_listening:
            raise ValidationError({'quiz': _('Select a listening quiz.')})

    @property
    def media_file_url(self) -> str:
        if self.audio_file:
            try:
                return self.audio_file.url
            except ValueError:
                return ''
        return ''


class ListeningQuestionGroup(models.Model):
    """Shared map/plan diagram and letter pool for IELTS labelling tasks (e.g. Q17–20)."""

    audio = models.ForeignKey(
        ListeningAudio,
        on_delete=models.CASCADE,
        related_name='question_groups',
        verbose_name=_('Audio section'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Title'),
        help_text=_('Shown to students, e.g. Questions 17–20.'),
    )
    instructions = RichTextField(
        blank=True,
        verbose_name=_('Instructions'),
        help_text=_('Task instructions shown above the map/plan.'),
    )
    question_type = models.CharField(
        max_length=32,
        choices=ListeningQuestionType.choices,
        default=ListeningQuestionType.MAP_LABELLING,
        verbose_name=_('Task type'),
    )
    diagram_image = models.ImageField(
        upload_to='portals/listening/diagrams/',
        blank=True,
        null=True,
        verbose_name=_('Map / plan image'),
        help_text=_('Upload the labelled diagram (map or floor plan).'),
    )
    option_pool = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Label options'),
        help_text=_('Letter pool shown as columns, e.g. ["A", "B", "C", "D", "E", "F", "G"].'),
    )

    class Meta:
        verbose_name = _('Listening question group')
        verbose_name_plural = _('Listening question groups')
        ordering = ('order', 'id')

    def __str__(self):
        label = (self.title or self.get_question_type_display() or '').strip()
        if label:
            return label[:80]
        return str(_('Listening group %(pk)s') % {'pk': self.pk or '—'})

    @property
    def pool_options(self) -> list[str]:
        return [str(item).strip() for item in (self.option_pool or []) if str(item).strip()]

    @property
    def is_label_group(self) -> bool:
        return self.question_type in LABEL_GROUP_QUESTION_TYPES

    def clean(self):
        super().clean()
        if self.question_type in LABEL_GROUP_QUESTION_TYPES:
            if len(self.pool_options) < 2:
                raise ValidationError(
                    {'option_pool': _('Add at least two label options (e.g. A through G).')},
                )
            if not self.diagram_image and not strip_tags(self.instructions or '').strip():
                raise ValidationError(
                    _('Upload a map/plan image or add instructions with the diagram.'),
                )
            return
        self.option_pool = []


def resolve_listening_question_options(question: 'ListeningQuestion') -> list[str]:
    if question.group_id and question.group:
        pool = question.group.pool_options
        if len(pool) >= 2:
            return pool
    return [
        str(item).strip()
        for item in (question.answer_options or [])
        if str(item).strip()
    ]


class ListeningQuestion(models.Model):
    """Gap-fill / short-answer task under a listening audio clip."""

    audio = models.ForeignKey(
        ListeningAudio,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('Audio section'),
    )
    group = models.ForeignKey(
        ListeningQuestionGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions',
        verbose_name=_('Question group'),
        help_text=_('Optional map/plan labelling group with a shared letter pool.'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
    )
    question = RichTextField(
        blank=True,
        verbose_name=_('Question'),
        help_text=_(
            'Written prompt for the student. Leave blank for a numbered answer line only, '
            'or add answer options below for a multiple-choice task.',
        ),
    )
    answer_options = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Answer options'),
        help_text=_('Optional JSON list of choices, e.g. ["Option A", "Option B"]. Leave empty for a text answer.'),
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
    spr_correct_answers = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('SPR correct answers'),
        help_text=_(
            'One or more accepted answers for typed (gap-fill) listening questions '
            '(e.g. ["library", "the library"]). Leave empty for multiple-choice tasks.'
        ),
    )
    spr_max_length = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('SPR max length'),
        help_text=_(
            'Optional character limit for the student input on typed answers. '
            'Leave blank for free-text answers.'
        ),
    )
    question_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Question config'),
        help_text=_('Word limits, alternatives, etc.'),
    )

    class Meta:
        verbose_name = _('Listening question')
        verbose_name_plural = _('Listening questions')
        ordering = ('order', 'id')

    def __str__(self):
        if self.question:
            return self.question[:80]
        return str(_('Question %(order)s') % {'order': self.order or '—'})

    @property
    def is_variant(self) -> bool:
        options = self.variant_options
        return len(options) >= 2

    @property
    def variant_options(self) -> list[str]:
        return resolve_listening_question_options(self)

    @property
    def in_label_group(self) -> bool:
        return bool(self.group_id and self.group and self.group.is_label_group)

    @property
    def spr_accepted_answers(self) -> list[str]:
        """Accepted typed answers: SPR list, else correct_answer + config alternatives."""
        from portals.utils.quiz_listening import build_listening_spr_answers

        return build_listening_spr_answers(self)

    @property
    def is_answerable(self) -> bool:
        if self.is_variant:
            return True
        if self.spr_accepted_answers:
            return True
        return bool(strip_tags(self.question or '').strip())

    def clean(self):
        super().clean()
        if self.group_id and self.group.audio_id != self.audio_id:
            raise ValidationError({'group': _('Question group must belong to the same audio clip.')})

        options = self.variant_options
        if self.group_id:
            pool = self.group.pool_options if self.group_id else []
            if len(pool) >= 2:
                options = pool
            elif len(options) < 2:
                raise ValidationError({
                    'group': _(
                        'Map/plan group needs at least two label options (e.g. A through G).'
                    ),
                })

        if len(options) >= 2:
            self.spr_correct_answers = None
            self.spr_max_length = None
            if self.in_label_group:
                self.answer_options = []
            from portals.utils.quiz_correct_option import sync_correct_option_fields

            resolved = sync_correct_option_fields(
                options,
                existing_index=self.correct_option_index,
                existing_answer=(self.correct_answer or '').strip(),
                match_answer=lambda opts, value: opts.index(value) if value in opts else None,
            )
            if resolved is None:
                raise ValidationError(
                    {'correct_answer': _('Select which answer option is correct.')},
                )
            idx, answer = resolved
            self.correct_option_index = idx
            self.correct_answer = answer
            return

        # Typed gap-fill (legacy single correct_answer / JSON answer) → SPR list.
        self.answer_options = []
        self.correct_option_index = 0
        from portals.utils.quiz_listening import build_listening_spr_answers

        spr_answers = build_listening_spr_answers(self)
        if not spr_answers:
            raise ValidationError({
                'spr_correct_answers': _('Add at least one correct answer for typed questions.'),
            })
        self.spr_correct_answers = spr_answers
        self.correct_answer = spr_answers[0][:500]

    def save(self, *args, **kwargs):
        options = self.variant_options
        if len(options) >= 2:
            if not self.in_label_group:
                self.answer_options = options
            else:
                self.answer_options = []
            self.spr_correct_answers = None
            self.spr_max_length = None
            from portals.utils.quiz_correct_option import sync_correct_option_fields

            resolved = sync_correct_option_fields(
                options,
                existing_index=self.correct_option_index,
                existing_answer=(self.correct_answer or '').strip(),
                match_answer=lambda opts, value: opts.index(value) if value in opts else None,
            )
            if resolved is not None:
                idx, answer = resolved
                self.correct_option_index = idx
                self.correct_answer = answer
        else:
            from portals.utils.quiz_listening import build_listening_spr_answers

            self.answer_options = []
            self.correct_option_index = 0
            spr_answers = build_listening_spr_answers(self)
            if spr_answers:
                self.spr_correct_answers = spr_answers
                self.correct_answer = spr_answers[0][:500]
        super().save(*args, **kwargs)

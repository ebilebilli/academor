from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _


class MockTestResult(models.Model):
    """Public mock-test result lookup by unique code (phone or assigned code)."""

    full_name = models.CharField(
        max_length=200,
        verbose_name=_('Full name'),
    )
    program_az = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Training program (AZ)'),
    )
    program_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Training program (EN)'),
    )
    program_ru = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Training program (RU)'),
    )
    code = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name=_('Code'),
        help_text=_('Mobile number or unique lookup code.'),
    )
    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Score'),
    )
    rank = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Rank'),
        help_text=_('Leave as-is when using automatic ranking.'),
    )
    show = models.BooleanField(
        default=False,
        verbose_name=_('Show in Top 5'),
        help_text=_('If enabled, this person can appear in the public Top 5 list.'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('Mock test result')
        verbose_name_plural = _('Mock test results')
        ordering = ('rank', '-score', 'full_name')

    def __str__(self):
        return f'{self.full_name} ({self.code})'

    def clean(self):
        super().clean()
        if not (self.program_az or self.program_en or self.program_ru):
            raise ValidationError(
                _('Fill in at least one training program field (AZ / EN / RU).')
            )

    def program_label(self, lang='az'):
        lang = (lang or 'az').lower()
        preferred = {
            'az': (self.program_az, self.program_en, self.program_ru),
            'en': (self.program_en, self.program_az, self.program_ru),
            'ru': (self.program_ru, self.program_en, self.program_az),
        }.get(lang, (self.program_az, self.program_en, self.program_ru))
        for value in preferred:
            text = (value or '').strip()
            if text:
                return text
        return ''

    def program_rank_key(self):
        """Stable key for auto-ranking within the same program."""
        return (
            (self.program_az or '').strip().casefold()
            or (self.program_en or '').strip().casefold()
            or (self.program_ru or '').strip().casefold()
        )

    def save(self, *args, **kwargs):
        if self.code:
            self.code = ' '.join(self.code.split())
        for field in ('program_az', 'program_en', 'program_ru'):
            value = getattr(self, field)
            if value:
                setattr(self, field, value.strip())
        super().save(*args, **kwargs)

    @classmethod
    def recalculate_ranks(cls):
        """Assign ranks by score within each training program (competition ranking)."""
        with transaction.atomic():
            rows = list(
                cls.objects.order_by('-score', 'id').only(
                    'id',
                    'score',
                    'program_az',
                    'program_en',
                    'program_ru',
                )
            )
            grouped = {}
            for row in rows:
                grouped.setdefault(row.program_rank_key() or '__empty__', []).append(row)

            updates = []
            for group_rows in grouped.values():
                prev_score = None
                prev_rank = 0
                for index, row in enumerate(group_rows, start=1):
                    if prev_score is None or row.score != prev_score:
                        rank = index
                        prev_score = row.score
                        prev_rank = rank
                    else:
                        rank = prev_rank
                    updates.append(cls(id=row.id, rank=rank))
            if updates:
                cls.objects.bulk_update(updates, ['rank'])
        return len(updates)

    @classmethod
    def lookup_by_code(cls, raw_code: str):
        code = ' '.join((raw_code or '').split())
        if not code:
            return None
        return cls.objects.filter(code__iexact=code).first()

    @classmethod
    def visible_program_tabs(cls, lang='az'):
        """Unique training programs that have at least one show=True result."""
        rows = cls.objects.filter(show=True).only(
            'program_az', 'program_en', 'program_ru',
        )
        tabs = {}
        for row in rows:
            key = row.program_rank_key()
            if not key or key in tabs:
                continue
            tabs[key] = {
                'key': key,
                'label': row.program_label(lang),
            }
        return sorted(tabs.values(), key=lambda item: item['label'].casefold())

    @classmethod
    def top5_for_program(cls, program_key: str):
        """Top 5 show=True rows for a training program key."""
        key = (program_key or '').strip().casefold()
        if not key:
            return []
        matched = []
        for row in (
            cls.objects.filter(show=True)
            .order_by('-score', 'rank', 'full_name')
            .iterator()
        ):
            if row.program_rank_key() == key:
                matched.append(row)
                if len(matched) >= 5:
                    break
        return matched

    @classmethod
    def top5_visible(cls):
        """Backward-compatible: first visible program's top 5, if any."""
        tabs = cls.visible_program_tabs()
        if not tabs:
            return []
        return cls.top5_for_program(tabs[0]['key'])


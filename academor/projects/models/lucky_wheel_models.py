from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def _pick_localized(obj, base: str, lang: str) -> str:
    lang = (lang or 'az').lower()
    order = {
        'az': (f'{base}_az', f'{base}_en', f'{base}_ru'),
        'en': (f'{base}_en', f'{base}_az', f'{base}_ru'),
        'ru': (f'{base}_ru', f'{base}_en', f'{base}_az'),
    }.get(lang, (f'{base}_az', f'{base}_en', f'{base}_ru'))
    for attr in order:
        value = (getattr(obj, attr, None) or '').strip()
        if value:
            return value
    return ''


class LuckyWheelPrize(models.Model):
    """Segment on the public lucky wheel — managed in admin."""

    label_line1_az = models.CharField(_('Label line 1 (AZ)'), max_length=40)
    label_line1_en = models.CharField(_('Label line 1 (EN)'), max_length=40, blank=True)
    label_line1_ru = models.CharField(_('Label line 1 (RU)'), max_length=40, blank=True)

    label_line2_az = models.CharField(_('Label line 2 (AZ)'), max_length=40, blank=True)
    label_line2_en = models.CharField(_('Label line 2 (EN)'), max_length=40, blank=True)
    label_line2_ru = models.CharField(_('Label line 2 (RU)'), max_length=40, blank=True)

    title_az = models.CharField(
        _('Result title (AZ)'),
        max_length=200,
        help_text=_('Shown in the result dialog, e.g. “You won 10% off”.'),
    )
    title_en = models.CharField(_('Result title (EN)'), max_length=200, blank=True)
    title_ru = models.CharField(_('Result title (RU)'), max_length=200, blank=True)

    code = models.CharField(
        _('Coupon code'),
        max_length=64,
        blank=True,
        help_text=_('Optional coupon code shown when the user wins.'),
    )
    weight = models.PositiveIntegerField(
        _('Weight'),
        default=10,
        help_text=_('Higher weight = more likely to land on this prize.'),
    )
    is_win = models.BooleanField(
        _('Winning prize'),
        default=True,
        help_text=_('If enabled, this outcome is treated as a win (confetti, coupon).'),
    )
    is_respin = models.BooleanField(
        _('Allow another spin'),
        default=False,
        help_text=_('If enabled, the user may spin again after this result.'),
    )
    is_active = models.BooleanField(_('Active'), default=True, db_index=True)
    order = models.PositiveIntegerField(_('Order'), default=0, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Lucky wheel prize')
        verbose_name_plural = _('Lucky wheel prizes')

    def __str__(self):
        line1 = self.label_line1_az or self.label_line1_en or f'#{self.pk}'
        line2 = self.label_line2_az or self.label_line2_en
        return f'{line1} {line2}'.strip() if line2 else line1

    def clean(self):
        super().clean()
        if self.is_respin and self.is_win:
            raise ValidationError(
                _('A respin outcome cannot also be marked as a winning prize.')
            )
        if self.is_win and not (self.code or '').strip():
            # Allow win without code (e.g. free delivery tracked manually)
            pass

    def label_lines(self, lang='az'):
        return [
            _pick_localized(self, 'label_line1', lang),
            _pick_localized(self, 'label_line2', lang),
        ]

    def result_title(self, lang='az'):
        return _pick_localized(self, 'title', lang)

    def to_wheel_dict(self, lang='az'):
        lines = self.label_lines(lang)
        return {
            'id': self.pk,
            'l': [lines[0], lines[1] or ''],
            'code': (self.code or '').strip() or None,
            'title': self.result_title(lang),
            'w': max(1, int(self.weight or 1)),
            'win': bool(self.is_win),
            'respin': bool(self.is_respin),
        }


class LuckyWheelSpin(models.Model):
    """One spin attempt — phone + prize landed."""

    phone = models.CharField(_('Mobile number'), max_length=30)
    phone_normalized = models.CharField(
        _('Normalized phone'),
        max_length=20,
        db_index=True,
        help_text=_('Digits only, used to prevent duplicate spins.'),
    )
    prize = models.ForeignKey(
        LuckyWheelPrize,
        on_delete=models.PROTECT,
        related_name='spins',
        verbose_name=_('Prize'),
    )
    prize_title = models.CharField(
        _('Prize title (snapshot)'),
        max_length=200,
        blank=True,
        help_text=_('Stored at spin time so admin prize edits do not rewrite history.'),
    )
    prize_code = models.CharField(
        _('Coupon code (snapshot)'),
        max_length=64,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Lucky wheel spin')
        verbose_name_plural = _('Lucky wheel spins')

    def __str__(self):
        return f'{self.phone} → {self.prize_title or self.prize_id}'

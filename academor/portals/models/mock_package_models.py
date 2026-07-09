from django.db import models
from django.utils.translation import gettext_lazy as _


class MockTestPackage(models.Model):
    """Purchasable mock-test credit bundle for customer portal users."""

    name_az = models.CharField(max_length=120, verbose_name=_('Name (AZ)'))
    name_en = models.CharField(max_length=120, blank=True, verbose_name=_('Name (EN)'))
    name_ru = models.CharField(max_length=120, blank=True, verbose_name=_('Name (RU)'))
    credits = models.PositiveIntegerField(
        verbose_name=_('Mock credits'),
        help_text=_('Number of mock tests granted after successful payment.'),
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Price (AZN)'),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('Mock test package')
        verbose_name_plural = _('Mock test packages')
        ordering = ('order', 'id')

    def localized_name(self, lang: str = 'az') -> str:
        lang = (lang or 'az')[:2]
        if lang == 'en' and self.name_en:
            return self.name_en
        if lang == 'ru' and self.name_ru:
            return self.name_ru
        return self.name_az

    def __str__(self):
        return f'{self.name_az} ({self.credits} × {self.price} AZN)'

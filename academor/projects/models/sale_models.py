from ckeditor.fields import RichTextField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Sale(models.Model):
    services = models.ManyToManyField(
        'Service',
        blank=True,
        related_name='sales',
        verbose_name=_('Services'),
        help_text=_('Optional. Leave empty for a general promotion.'),
    )
    name_az = models.CharField(
        max_length=255,
        verbose_name=_('Name (AZ)'),
    )
    name_en = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Name (EN)'),
    )
    name_ru = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Name (RU)'),
    )
    description_az = RichTextField(
        blank=True,
        verbose_name=_('Description (AZ)'),
    )
    description_en = RichTextField(
        blank=True,
        verbose_name=_('Description (EN)'),
    )
    description_ru = RichTextField(
        blank=True,
        verbose_name=_('Description (RU)'),
    )
    percent = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
        null=True,
        blank=True,
        verbose_name=_('Discount (%)'),
        help_text=_('Optional. Leave empty for a general promotion or event without a discount.'),
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('End date'),
        help_text=_('Optional. Promotion is hidden from the homepage after this date.'),
    )
    apply_to_service_prices = models.BooleanField(
        default=False,
        verbose_name=_('Apply discount to service prices'),
        help_text=_(
            'When enabled, the discount percentage is deducted from the prices '
            'of the selected services.'
        ),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )

    class Meta:
        verbose_name = _('Sale')
        verbose_name_plural = _('Sales')
        ordering = ('-created_at',)

    def __str__(self):
        return self.name_az

from django.db import models
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField

from projects.service_category_icons import SERVICE_CATEGORY_ICON_CHOICES
from projects.utils import SluggedModel


class Service(SluggedModel):
    name_az = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Category name (AZ)'
    )
    name_en = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Category name (EN)'
    )
    name_ru = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Category name (RU)'
    )
    description_az = RichTextField(
        blank=True,
        verbose_name='Description (AZ)'
    )
    description_en = RichTextField(
        blank=True,
        verbose_name='Description (EN)'
    )
    description_ru = RichTextField(
        blank=True,
        verbose_name='Description (RU)'
    )
    duration_months_az = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Duration (AZ)'
    )
    duration_months_en = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Duration (EN)'
    )
    duration_months_ru = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Duration (RU)'
    )
    lesson_count_az = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Lesson counts (AZ)'
    )
    lesson_count_en = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Lesson counts (EN)'
    )
    lesson_count_ru = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Lesson counts (RU)'
    )
    has_certificate = models.BooleanField(
        default=True,
        verbose_name='Certificate'
    )
    is_online = models.BooleanField(
        default=True,
        verbose_name='Online'
    )
    is_offline = models.BooleanField(
        default=True,
        verbose_name='Offline'
    )
    instructors = models.ManyToManyField(
        'Team',
        blank=True,
        related_name='services',
        verbose_name='Trainers',
        help_text='Team members shown on the course detail page (Trainers tab).',
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Order'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )
    show_on_main_page = models.BooleanField(
        default=True,
        verbose_name=_('Show on home page'),
        help_text=_(
            'If enabled, this course appears in the "Our Services" grid on the homepage.'
        ),
    )
    card_icon = models.CharField(
        max_length=80,
        blank=True,
        default='',
        choices=SERVICE_CATEGORY_ICON_CHOICES,
        verbose_name=_('Card icon'),
        help_text=_(
            'Font Awesome 5 icon on service cards (home page and courses list). '
            'Choose a preset matching the program (IELTS, GMAT, Speaking, etc.).'
        ),
    )
    price = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Price (AZN)'),
        help_text=_('Course fee in AZN. Leave empty to hide the pay button.'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    tags = models.ManyToManyField(
        'ContentTag',
        blank=True,
        related_name='services',
        verbose_name='Tags',
    )

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ('order', 'id')

    def get_slug_source(self) -> str:
        return self.name_az

    def __str__(self):
        return self.name_az or 'Service'

    @property
    def has_active_price_packages(self):
        return self.price_packages.filter(is_active=True, price__gt=0).exists()


class CoursePricePackage(models.Model):
    """Payable pricing option for a course (one course may have several packages)."""

    course = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='price_packages',
        verbose_name=_('Course'),
    )
    name_az = models.CharField(max_length=255, verbose_name=_('Name (AZ)'))
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
    months = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Months'),
        help_text=_('Course length in months (used in the training agreement).'),
    )
    lesson_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Number of lessons'),
    )
    lesson_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Minutes per lesson'),
        help_text=_('Duration of a single lesson in minutes.'),
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Price (AZN)'),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    is_premium = models.BooleanField(
        default=False,
        verbose_name=_('Premium'),
        help_text=_('Highlight this package with a distinct card style when selected.'),
    )
    show_on_homepage = models.BooleanField(
        default=False,
        verbose_name=_('Show on homepage'),
        help_text=_(
            'If enabled, this package appears in the homepage "Most in demand" price carousel.'
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Course price package')
        verbose_name_plural = _('Course price packages')
        ordering = ('order', 'id')

    def __str__(self):
        label = self.name_az or self.name_en or self.name_ru or f'Package #{self.pk}'
        return f'{label} — {self.price} AZN'

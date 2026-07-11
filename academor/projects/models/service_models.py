from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField

from projects.service_category_icons import SERVICE_CATEGORY_ICON_CHOICES
from projects.utils import SluggedModel

MOCK_TEST_SERVICE_Q = Q(ielts_mock_test=True) | Q(sat_mock_test=True)
MOCK_TEST_SERVICE_VIA_COURSE_Q = (
    Q(course__ielts_mock_test=True) | Q(course__sat_mock_test=True)
)


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
    ielts_mock_test = models.BooleanField(
        default=False,
        verbose_name=_('IELTS mock test'),
        help_text=_(
            'If enabled, this service appears under Mock tests and uses IELTS mock pricing.'
        ),
    )
    sat_mock_test = models.BooleanField(
        default=False,
        verbose_name=_('SAT mock test'),
        help_text=_(
            'If enabled, this service appears under Mock tests and uses SAT mock pricing.'
        ),
    )
    bullet_list_az = models.TextField(
        blank=True,
        null=True,
        validators=[MaxLengthValidator(2000)],
        verbose_name='Maddələr siyahısı (AZ)',
        help_text='Hər sətirdə bir maddə yazın (bullet list).',
    )
    bullet_list_en = models.TextField(
        blank=True,
        null=True,
        validators=[MaxLengthValidator(2000)],
        verbose_name='Maddələr siyahısı (EN)',
        help_text='One item per line (bullet list).',
    )
    bullet_list_ru = models.TextField(
        blank=True,
        null=True,
        validators=[MaxLengthValidator(2000)],
        verbose_name='Maddələr siyahısı (RU)',
        help_text='Один пункт на строку (маркированный список).',
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
        constraints = [
            models.CheckConstraint(
                condition=~Q(ielts_mock_test=True, sat_mock_test=True),
                name='service_single_mock_test_type',
            ),
        ]

    def get_slug_source(self) -> str:
        return self.name_az

    def __str__(self):
        return self.name_az or 'Service'

    @property
    def is_mock_test(self) -> bool:
        return bool(self.ielts_mock_test or self.sat_mock_test)

    def clean(self):
        super().clean()
        if self.ielts_mock_test and self.sat_mock_test:
            raise ValidationError(
                _('Select only one mock test type: IELTS or SAT.'),
            )

    @property
    def has_active_price_packages(self):
        return self.price_packages.filter(is_active=True, price__gt=0).exists()


class CoursePricePackage(models.Model):
    """Payable pricing option for a course (one course may have several packages)."""

    class PackageTab(models.TextChoices):
        GROUP_STANDARD = (
            'group_standard',
            _('Group lessons — Standard'),
        )
        GROUP_INTENSIVE = (
            'group_intensive',
            _('Group lessons — Intensive'),
        )
        INDIVIDUAL_STANDARD = (
            'individual_standard',
            _('Individual lessons — Standard'),
        )
        INDIVIDUAL_INTENSIVE = (
            'individual_intensive',
            _('Individual lessons — Intensive'),
        )
        FULL_PACKAGE_GROUP = (
            'full_package_group',
            _('Full package — Group'),
        )
        FULL_PACKAGE_INDIVIDUAL = (
            'full_package_individual',
            _('Full package — Individual'),
        )
        FULL_PACKAGE_INSTALLMENT = (
            'full_package_installment',
            _('Full package — Installments'),
        )
        MOCK_TEST = (
            'mock_test',
            _('Mock Test'),
        )

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
    credits = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Mock test credits'),
        help_text=_(
            'Required when the selected course is an IELTS or SAT mock test service.'
        ),
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Price (AZN)'),
    )
    package_tab = models.CharField(
        max_length=32,
        choices=PackageTab.choices,
        default=PackageTab.GROUP_STANDARD,
        db_index=True,
        verbose_name=_('Payment tab'),
        help_text=_(
            'Which tab on the course payment section shows this package.'
        ),
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

    def clean(self):
        super().clean()
        course = self.course
        if course_id := getattr(self, 'course_id', None):
            if course is None or getattr(course, 'pk', None) != course_id:
                course = Service.objects.filter(pk=course_id).first()
        if course and course.is_mock_test:
            self.months = None
            self.lesson_count = None
            self.lesson_minutes = None
            if not self.credits or self.credits < 1:
                raise ValidationError(
                    {'credits': _('Mock test credits are required for this course.')},
                )
        elif self.credits:
            self.credits = None

    def save(self, *args, **kwargs):
        if self.course_id:
            course = self.course
            if course is None or getattr(course, 'pk', None) != self.course_id:
                course = Service.objects.filter(pk=self.course_id).first()
            if course and course.is_mock_test:
                self.months = None
                self.lesson_count = None
                self.lesson_minutes = None
        super().save(*args, **kwargs)

    def __str__(self):
        label = self.name_az or self.name_en or self.name_ru or f'Package #{self.pk}'
        return f'{label} — {self.price} AZN'

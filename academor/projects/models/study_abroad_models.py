from django.db import models
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from projects.utils import SluggedModel


class AbroadModel(SluggedModel):
    name_az = models.CharField(
        max_length=120,
        blank=True,
        default='',
        verbose_name='Name (AZ)'
    )
    name_en = models.CharField(
        max_length=120,
        blank=True,
        default='',
        verbose_name='Name (EN)'
    )
    name_ru = models.CharField(
        max_length=120,
        blank=True,
        default='',
        verbose_name='Name (RU)'
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
    img = models.ImageField(
        upload_to='abroad/',
        verbose_name='Image'
    )
    img_thumb = ImageSpecField(
        source='img',
        processors=[ResizeToFit(180, 180)],
        format='WEBP',
        options={'quality': 75},
    )
    detail_page_img = models.ImageField(
        upload_to='abroad/detail/',
        null=True,
        blank=True,
        verbose_name='Detail page image'
    )
    detail_page_img_hero = ImageSpecField(
        source='detail_page_img',
        processors=[ResizeToFit(1280, 640)],
        format='WEBP',
        options={'quality': 80},
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )
    show_on_main_page = models.BooleanField(
        default=True,
        verbose_name=_('Show on home page'),
        help_text=_(
            'If enabled, this country and its linked universities appear in the study-abroad block on the homepage.'
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Abroad item'
        verbose_name_plural = 'Abroad items'
        ordering = ('id',)

    def get_slug_source(self) -> str:
        base = (self.name_az or self.name_en or self.name_ru or '').strip()
        if base:
            return base
        if self.pk:
            return f'abroad-{self.pk}'
        return 'abroad'

    def __str__(self):
        return self.name_az or self.name_en or self.name_ru or f'Abroad item #{self.pk}'


class StudyAbroadSection(models.Model):
    text_az = RichTextField(
        blank=True,
        verbose_name='Text (AZ)'
    )
    text_en = RichTextField(
        blank=True,
        verbose_name='Text (EN)'
    )
    text_ru = RichTextField(
        blank=True,
        verbose_name='Text (RU)'
    )
    advantages_title_az = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Advantages heading (AZ)',
    )
    advantages_title_en = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Advantages heading (EN)',
    )
    advantages_title_ru = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Advantages heading (RU)',
    )

    class Meta:
        verbose_name = 'Study Abroad Section Text'
        verbose_name_plural = 'Study Abroad Section Text'

    def __str__(self):
        return 'Study Abroad Section'


class StudyAbroadAdvantage(models.Model):
    """Icon highlights shown under the study-abroad hero (home + /abroad/)."""

    section = models.ForeignKey(
        StudyAbroadSection,
        on_delete=models.CASCADE,
        related_name='advantage_items',
        verbose_name='Section',
    )
    icon = models.CharField(
        max_length=80,
        default='fa-star',
        verbose_name='Icon (Font Awesome)',
        help_text='Font Awesome 5 class, e.g. fa-certificate',
    )
    title_az = models.CharField(max_length=160, verbose_name='Label (AZ)')
    title_en = models.CharField(max_length=160, blank=True, verbose_name='Label (EN)')
    title_ru = models.CharField(max_length=160, blank=True, verbose_name='Label (RU)')
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Study abroad advantage'
        verbose_name_plural = 'Study abroad advantages'

    def __str__(self):
        return (self.title_az or self.title_en or f'Advantage #{self.pk}')[:80]


class University(models.Model):
    name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Name',
    )
    slug = models.SlugField(
        max_length=150,
        null=True,
        blank=True,
        unique=True,
        verbose_name='URL slug',
    )
    description_az = RichTextField(
        null=True,
        blank=True,
        verbose_name='Description (AZ)',
    )
    description_en = RichTextField(
        null=True,
        blank=True,
        verbose_name='Description (EN)',
    )
    description_ru = RichTextField(
        null=True,
        blank=True,
        verbose_name='Description (RU)',
    )
    study_abroad = models.ForeignKey(
        'AbroadModel',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='universities',
        verbose_name='Study abroad country',
    )
    website = models.URLField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name='Website URL',
    )
    flag = models.ImageField(
        upload_to='universities/',
        verbose_name='Flag image'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )

    class Meta:
        verbose_name = 'University'
        verbose_name_plural = 'Universities'
        ordering = ('id',)

    def __str__(self):
        if self.name and str(self.name).strip():
            return str(self.name).strip()
        return f'University #{self.pk}'

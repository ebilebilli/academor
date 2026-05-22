from django.db import models
from ckeditor.fields import RichTextField


class About(models.Model):
    description_az = RichTextField(verbose_name='Text (AZ)')
    description_en = RichTextField(verbose_name='Text (EN)')
    description_ru = RichTextField(verbose_name='Text (RU)')

    class Meta:
        verbose_name = 'About'
        verbose_name_plural = 'About'

    def __str__(self):
        return 'About'


class AboutWhyItem(models.Model):
    """Why Academor highlights shown below the image on the About page."""

    icon = models.CharField(
        max_length=80,
        default='fa-star',
        verbose_name='Icon (Font Awesome)',
        help_text='Font Awesome 5 class, e.g. fa-graduation-cap',
    )
    title_az = models.CharField(max_length=160, verbose_name='Title (AZ)')
    title_en = models.CharField(max_length=160, blank=True, verbose_name='Title (EN)')
    title_ru = models.CharField(max_length=160, blank=True, verbose_name='Title (RU)')
    text_az = models.CharField(max_length=280, blank=True, verbose_name='Text (AZ)')
    text_en = models.CharField(max_length=280, blank=True, verbose_name='Text (EN)')
    text_ru = models.CharField(max_length=280, blank=True, verbose_name='Text (RU)')
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Why Academor item'
        verbose_name_plural = 'Why Academor items'

    def __str__(self):
        return (self.title_az or self.title_en or f'Why #{self.pk}')[:80]

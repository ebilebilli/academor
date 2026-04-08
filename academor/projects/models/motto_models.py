from django.db import models
from django.core.validators import MaxLengthValidator
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)


class Tagline(models.Model):
    # Small heading (e.g. "Best Online Courses")
    heading_small_az = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Hero small heading (AZ)',
    )
    heading_small_en = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Hero small heading (EN)',
    )
    heading_small_ru = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Hero small heading (RU)',
    )

    # Main heading (e.g. "The Best Online Learning Platform")
    heading_main_az = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Hero main heading (AZ)',
    )
    heading_main_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Hero main heading (EN)',
    )
    heading_main_ru = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Hero main heading (RU)',
    )

    # Body/description text under the headings
    body_az = models.TextField(
        validators=[MaxLengthValidator(400)],
        blank=True,
        verbose_name='Hero description (AZ)',
    )
    body_en = models.TextField(
        validators=[MaxLengthValidator(400)],
        blank=True,
        verbose_name='Hero description (EN)',
    )
    body_ru = models.TextField(
        validators=[MaxLengthValidator(400)],
        blank=True,
        verbose_name='Hero description (RU)',
    )

    class Meta:
        verbose_name = 'Tagline'
        verbose_name_plural = 'Tagline)'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Tagline'


class HeroSlide(models.Model):
    image = models.ImageField(
        upload_to='images/',
        verbose_name='Slide image',
    )
    heading_small_az = models.CharField(max_length=150, blank=True, verbose_name='Small heading (AZ)')
    heading_small_en = models.CharField(max_length=150, blank=True, verbose_name='Small heading (EN)')
    heading_small_ru = models.CharField(max_length=150, blank=True, verbose_name='Small heading (RU)')

    heading_main_az = models.CharField(max_length=200, blank=True, verbose_name='Main heading (AZ)')
    heading_main_en = models.CharField(max_length=200, blank=True, verbose_name='Main heading (EN)')
    heading_main_ru = models.CharField(max_length=200, blank=True, verbose_name='Main heading (RU)')

    body_az = models.TextField(validators=[MaxLengthValidator(400)], blank=True, verbose_name='Description (AZ)')
    body_en = models.TextField(validators=[MaxLengthValidator(400)], blank=True, verbose_name='Description (EN)')
    body_ru = models.TextField(validators=[MaxLengthValidator(400)], blank=True, verbose_name='Description (RU)')

    order = models.PositiveSmallIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

    class Meta:
        verbose_name = 'Hero Slide'
        verbose_name_plural = 'Hero Slides'
        ordering = ['order', 'id']

    def delete_files(self):
        if not self.image:
            return
        image_name = self.image.name
        try:
            storage = default_storage
            webp_name = image_name.rsplit('.', 1)[0] + '.webp'
            if storage.exists(webp_name):
                storage.delete(webp_name)
            if storage.exists(image_name):
                storage.delete(image_name)
        except Exception as e:
            logger.error(f"[HERO SLIDE DELETE] Error deleting files: {e}")

    def delete(self, *args, **kwargs):
        self.delete_files()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.heading_main_az or self.heading_main_en or f'HeroSlide #{self.pk}'

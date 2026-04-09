from django.db import models
from django.core.validators import MaxLengthValidator


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

from django.db import models
from django.core.validators import MaxLengthValidator


class About(models.Model):
    main_title_az = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name='Main title (AZ)'
    )
    main_title_en = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name='Main title (EN)'
    )
    main_title_ru = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name='Main title (RU)'
    )
    second_title_az = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='Subtitle (AZ)'
    )
    second_title_en = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='Subtitle (EN)'
    )
    second_title_ru = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='Subtitle (RU)'
    )
    description_az = models.TextField(
        validators=[MaxLengthValidator(4000)],
        verbose_name='Text (AZ)'
    )
    description_en = models.TextField(
        validators=[MaxLengthValidator(4000)],
        verbose_name='Text (EN)'
    )
    description_ru = models.TextField(
        validators=[MaxLengthValidator(4000)],
        verbose_name='Text (RU)'
    )

    class Meta:
        verbose_name = 'About'
        verbose_name_plural = 'About'

    def __str__(self):
        return self.main_title_az or 'About'

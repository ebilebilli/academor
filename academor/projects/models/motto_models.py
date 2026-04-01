from django.db import models
from django.core.validators import MaxLengthValidator


class Tagline(models.Model):
    text_az = models.TextField(
        validators=[MaxLengthValidator(220)],
        verbose_name='Tagline (AZ)'
    )
    text_en = models.TextField(
        validators=[MaxLengthValidator(220)],
        verbose_name='Tagline (EN)'
    )
    text_ru = models.TextField(
        validators=[MaxLengthValidator(220)],
        verbose_name='Tagline (RU)'
    )

    class Meta:
        verbose_name = 'Tagline'
        verbose_name_plural = 'Taglines'

    def __str__(self):
        return 'Tagline'
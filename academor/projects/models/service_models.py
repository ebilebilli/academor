from django.db import models
from django.core.validators import MaxLengthValidator


class Program(models.Model):
    title_az = models.CharField(
        max_length=250,
        verbose_name='Service title (AZ)'
    )
    title_en = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Service title (EN)'
    )
    title_ru = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Service title (RU)'
    )
    description_az = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(800)],
        verbose_name='Service description (AZ)',
    )
    description_en = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(800)],
        verbose_name='Service description (EN)',
    )
    description_ru = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(800)],
        verbose_name='Service description (RU)',
    )
    url = models.URLField(
        null=True,
        blank=True,
        verbose_name='Link'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering  = ['-created_at']
    

    def __str__(self):
        return self.title_az or 'Service'

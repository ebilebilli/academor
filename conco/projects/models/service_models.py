from django.db import models
from django.core.validators import MaxLengthValidator


class Service(models.Model):
    title_az = models.CharField(
        max_length=250,
        verbose_name='Service adı (AZ)'
    )
    title_en = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Service adı (EN)'
    )
    title_ru = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Service adı (RU)'
    )
    description_az = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(800)],
        verbose_name='Service haqqında (AZ)',
    )
    description_en = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(800)],
        verbose_name='Service haqqında (EN)',
    )
    description_ru = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(800)],
        verbose_name='Service haqqında (RU)',
    )
    url = models.URLField(
        null=True,
        blank=True,
        verbose_name=('Link')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaradılma tarixi'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Servis aktivliyi'
    )

    class Meta:
        verbose_name = 'Servis'
        verbose_name_plural = 'Servislər'
        ordering  = ['-created_at']
    

    def __str__(self):
        return self.title_az or 'Servis'

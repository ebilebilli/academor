from django.db import models
from django.core.validators import MaxLengthValidator

from projects.utils import SluggedModel


class CareerOpening(SluggedModel):
    title_az = models.CharField(
        max_length=250,
        verbose_name='Vacancy title (AZ)'
    )
    title_en = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Vacancy title (EN)'
    )
    title_ru = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Vacancy title (RU)'
    )
    description_az = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(8000)],
        verbose_name='Vacancy description (AZ)',
    )
    description_en = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(8000)],
        verbose_name='Vacancy description (EN)',
    )
    description_ru = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(8000)],
        verbose_name='Vacancy description (RU)',
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
        verbose_name = 'Vacancy'
        verbose_name_plural = 'Vacancies'
        ordering  = ['-created_at']
    
    def get_slug_source(self) -> str:
        return self.title_az

    def __str__(self):
        return self.title_az or 'Vacancy'

from django.db import models
from django.core.validators import MaxLengthValidator


class Instructor(models.Model):
    name_az = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        validators=[MaxLengthValidator(120)],
        verbose_name='Partner name (AZ)'
    )
    name_en = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        validators=[MaxLengthValidator(120)],
        verbose_name='Partner name (EN)'
    )
    name_ru = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        validators=[MaxLengthValidator(120)],
        verbose_name='Partner name (RU)'
    )
    instagram = models.URLField(
        null=True,
        blank=True,
        verbose_name='(Instagram)'
    )
    facebook = models.URLField(
        null=True,
        blank=True,
        verbose_name=('Facebook')
    )
    linkedn = models.URLField(
        null=True,
        blank=True,
        verbose_name='LinkedIn'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Instructor'
        verbose_name_plural = 'Instructors'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name_az or 'Instructor'

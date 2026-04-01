from django.db import models
from django.core.validators import MaxLengthValidator


class Team(models.Model):
    image = models.ImageField(
        upload_to='team/',
        null=True,
        blank=True,
        verbose_name='Image',
    )
    name = models.CharField(
        max_length=120,
        verbose_name='Name',
    )
    role = models.CharField(
        max_length=120,
        verbose_name='Role',
    )
    description = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(1000)],
        verbose_name='Description',
    )
    instagram = models.URLField(
        null=True,
        blank=True,
        verbose_name='Instagram',
    )
    facebook = models.URLField(
        null=True,
        blank=True,
        verbose_name='Facebook',
    )
    linkedin = models.URLField(
        null=True,
        blank=True,
        verbose_name='LinkedIn',
    )
    tiktok = models.URLField(
        null=True,
        blank=True,
        verbose_name='TikTok',
    )
    youtube = models.URLField(
        null=True,
        blank=True,
        verbose_name='YouTube',
    )

    class Meta:
        verbose_name = 'Team member'
        verbose_name_plural = 'Team'
        ordering = ('id',)

    def __str__(self):
        return f'{self.name} ({self.role})'

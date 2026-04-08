from django.db import models
from ckeditor.fields import RichTextField


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
    description = RichTextField(
        null=True,
        blank=True,
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

    descriptor = models.FileField(
        upload_to='team/descriptors/',
        null=True,
        blank=True,
        verbose_name='Description file',
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Order',
    )

    class Meta:
        verbose_name = 'Team member'
        verbose_name_plural = 'Team'
        ordering = ('order', 'id')

    def __str__(self):
        return f'{self.name} ({self.role})'

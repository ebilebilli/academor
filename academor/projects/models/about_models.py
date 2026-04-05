from django.db import models
from ckeditor.fields import RichTextField


class About(models.Model):
    description_az = RichTextField(verbose_name='Text (AZ)')
    description_en = RichTextField(verbose_name='Text (EN)')
    description_ru = RichTextField(verbose_name='Text (RU)')

    class Meta:
        verbose_name = 'About'
        verbose_name_plural = 'About'

    def __str__(self):
        return 'About'

from django.db import models

from projects.utils.abstract_models import SluggedModel


class ContentTag(SluggedModel):
    name_az = models.CharField(max_length=100, verbose_name='Name (AZ)')
    name_en = models.CharField(max_length=100, blank=True, verbose_name='Name (EN)')
    name_ru = models.CharField(max_length=100, blank=True, verbose_name='Name (RU)')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ('order', 'name_az', 'id')

    def __str__(self):
        return self.name_az or self.slug

    def get_slug_source(self) -> str:
        return (self.name_az or self.name_en or self.name_ru or '').strip()

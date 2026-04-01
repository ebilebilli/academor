from django.db import models
from django.core.validators import MaxLengthValidator

from projects.utils import SluggedModel


class ServiceCategory(SluggedModel):
    name_az = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Category name (AZ)'
    )
    name_en = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Category name (EN)'
    )
    name_ru = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Category name (RU)'
    )

    class Meta:
        verbose_name = 'Service category'
        verbose_name_plural = 'Service categories'
    
    def get_slug_source(self) -> str:
        return self.name_az

    def __str__(self):
        return self.name_az or 'Category'


class Service(SluggedModel):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name='services',
        verbose_name='Service category'
    )
    name_az = models.CharField(
        max_length=250,
        verbose_name='Name (AZ)'
    )
    name_en = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Name (EN)'
    )
    name_ru = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Name (RU)'
    )
    description_az = models.TextField(
        validators=[MaxLengthValidator(5000)],
        verbose_name='Service description (AZ)'
    )
    description_en = models.TextField(
        validators=[MaxLengthValidator(5000)],
        null=True,
        blank=True,
        verbose_name='Service description (EN)'
    )
    description_ru = models.TextField(
        validators=[MaxLengthValidator(5000)],
        null=True,
        blank=True,
        verbose_name='Service description (RU)'
    )
    url = models.URLField(
        null=True,
        blank=True,
        verbose_name='URL'
    )
    is_completed = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name='Completed'
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name='Active'
    )
    speacial_project = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name='Featured'
    )
    on_main_page = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name='Show on home page'
    )
    project_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Service date'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    def get_slug_source(self) -> str:
        return self.name_az

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering  = ['-created_at']

    def __str__(self):
        return self.name_az

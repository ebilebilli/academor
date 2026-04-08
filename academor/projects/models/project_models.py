from django.db import models

from ckeditor.fields import RichTextField

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
    description_az = RichTextField(
        blank=True,
        verbose_name='Description (AZ)'
    )
    description_en = RichTextField(
        blank=True,
        verbose_name='Description (EN)'
    )
    description_ru = RichTextField(
        blank=True,
        verbose_name='Description (RU)'
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
        verbose_name = 'Service category'
        verbose_name_plural = 'Service categories'

    def get_slug_source(self) -> str:
        return self.name_az

    def __str__(self):
        return self.name_az or 'Category'


class ServiceHighlight(models.Model):
    title_az = models.CharField(
        max_length=160,
        null=True,
        blank=True,
        verbose_name='Title (AZ)'
    )
    title_en = models.CharField(
        max_length=160,
        null=True,
        blank=True,
        verbose_name='Title (EN)'
    )
    title_ru = models.CharField(
        max_length=160,
        null=True,
        blank=True,
        verbose_name='Title (RU)'
    )
    description_az = models.TextField(
        null=True,
        blank=True,
        max_length=200,
        verbose_name='Description (AZ)'
    )
    description_en = models.TextField(
        null=True,
        blank=True,
        max_length=200,
        verbose_name='Description (EN)'
    )
    description_ru = models.TextField(
        null=True,
        blank=True,
        max_length=200,
        verbose_name='Description (RU)'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Order'
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
        verbose_name = 'Service highlight'
        verbose_name_plural = 'Service highlights'
        ordering = ('order', 'id')

    def __str__(self):
        return self.title_az or self.title_en or self.title_ru or f'Highlight #{self.pk}'


class AbroadModel(models.Model):
    name = models.CharField(
        max_length=120,
        verbose_name='Name'
    )
    description_az = RichTextField(
        blank=True,
        verbose_name='Description (AZ)'
    )
    description_en = RichTextField(
        blank=True,
        verbose_name='Description (EN)'
    )
    description_ru = RichTextField(
        blank=True,
        verbose_name='Description (RU)'
    )
    img = models.ImageField(
        upload_to='abroad/',
        verbose_name='Image'
    )
    detail_page_img = models.ImageField(
        upload_to='abroad/detail/',
        null=True,
        blank=True,
        verbose_name='Detail page image'
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
        verbose_name = 'Abroad item'
        verbose_name_plural = 'Abroad items'
        ordering = ('id',)

    def __str__(self):
        return self.name


class StudyAbroadSection(models.Model):
    text_az = RichTextField(
        blank=True,
        verbose_name='Text (AZ)'
    )
    text_en = RichTextField(
        blank=True,
        verbose_name='Text (EN)'
    )
    text_ru = RichTextField(
        blank=True,
        verbose_name='Text (RU)'
    )

    class Meta:
        verbose_name = 'Study Abroad Section Text'
        verbose_name_plural = 'Study Abroad Section Text'

    def __str__(self):
        return 'Study Abroad Section'


class University(models.Model):
    flag = models.ImageField(
        upload_to='universities/',
        verbose_name='Flag image'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )

    class Meta:
        verbose_name = 'University'
        verbose_name_plural = 'Universities'
        ordering = ('id',)

    def __str__(self):
        return f'University #{self.pk}'

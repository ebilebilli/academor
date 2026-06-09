from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


class Team(models.Model):
    image = models.ImageField(
        upload_to='team/',
        null=True,
        blank=True,
        verbose_name='Image',
    )
    image_card = ImageSpecField(
        source='image',
        processors=[ResizeToFit(400, 400)],
        format='WEBP',
        options={'quality': 75},
    )
    image_detail = ImageSpecField(
        source='image',
        processors=[ResizeToFit(640, 854)],
        format='WEBP',
        options={'quality': 80},
    )
    name = models.CharField(
        max_length=120,
        verbose_name='Name',
    )
    slug = models.SlugField(
        max_length=150,
        unique=True,
        verbose_name='URL slug',
    )
    role = models.CharField(
        max_length=120,
        verbose_name='Role',
    )
    description_az = RichTextField(
        null=True,
        blank=True,
        verbose_name='Description (AZ)',
    )
    description_en = RichTextField(
        null=True,
        blank=True,
        verbose_name='Description (EN)',
    )
    description_ru = RichTextField(
        null=True,
        blank=True,
        verbose_name='Description (RU)',
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

    def _unique_slug_from_name(self) -> str:
        base = slugify(self.name.strip()) or 'member'
        if len(base) > 140:
            base = base[:140]
        slug = base
        n = 2
        qs = Team.objects.exclude(pk=self.pk) if self.pk else Team.objects.all()
        while qs.filter(slug=slug).exists():
            suffix = f'-{n}'
            slug = (base[: max(1, 150 - len(suffix))] + suffix)[:150]
            n += 1
        return slug

    def save(self, *args, **kwargs):
        self.slug = self._unique_slug_from_name()
        super().save(*args, **kwargs)

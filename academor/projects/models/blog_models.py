from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from projects.utils.abstract_models import SluggedModel

_ON_TOP_MAX = 2


class BlogPost(SluggedModel):
    name_az = models.CharField(
        max_length=200, 
        verbose_name='Name (AZ)'
    )
    name_en = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Name (EN)'
    )
    name_ru = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Name (RU)'
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
    date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date',
        help_text='Display date (set manually).',
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Created at'
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name='Active'
    )
    on_top = models.BooleanField(
        default=False,
        verbose_name='On top',
        help_text=format_lazy(
            _('Pinned posts appear first (maximum {max:d} allowed).'),
            max=_ON_TOP_MAX,
        ),
    )
    on_main_page = models.BooleanField(
        default=False,
        verbose_name='On main page',
        help_text='Show this post on the homepage.',
    )

    class Meta:
        verbose_name = 'Blog post'
        verbose_name_plural = 'Blog'
        ordering = ('-on_top', '-date', '-id')

    def __str__(self):
        return self.name_az or self.slug

    def get_slug_source(self) -> str:
        return (self.name_az or self.name_en or self.name_ru or '').strip()

    def clean(self):
        super().clean()
        if not self.on_top:
            return
        qs = BlogPost.objects.filter(on_top=True)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.count() >= _ON_TOP_MAX:
            raise ValidationError({
                'on_top': _(
                    'You can mark at most %(max)d posts as featured (“On top”). '
                    'Uncheck “On top” on another post first.'
                ) % {'max': _ON_TOP_MAX},
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BlogPostImage(models.Model):
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Blog post',
    )
    image = models.ImageField(upload_to='blog/', verbose_name='Image')
    image_card = ImageSpecField(
        source='image',
        processors=[ResizeToFit(400, 400)],
        format='WEBP',
        options={'quality': 75},
    )
    image_large = ImageSpecField(
        source='image',
        processors=[ResizeToFit(800, 800)],
        format='WEBP',
        options={'quality': 80},
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(5)],
        verbose_name='Order',
        help_text='0 = cover (first). Max 6 images total.',
    )

    class Meta:
        verbose_name = 'Blog post image'
        verbose_name_plural = 'Blog post images'
        ordering = ('order', 'id')

    def __str__(self):
        return f'{self.post} — image #{self.order}'

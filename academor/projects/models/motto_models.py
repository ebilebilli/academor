from django.db import models
from django.core.validators import MaxLengthValidator
from django.utils.translation import gettext_lazy as _


class TaglinePage(models.TextChoices):
    ABOUT = 'about', _('About page')
    CONTACT = 'contact', _('Contact page')
    SERVICE = 'service', _('Services page')
    COURSES = 'courses', _('Courses page')
    TESTS = 'tests', _('Tests page')
    ABROAD = 'abroad', _('Study abroad page')
    BLOG = 'blog', _('Blog page')
    TEAM = 'team', _('Team page')


class Tagline(models.Model):
    page = models.CharField(
        max_length=20,
        choices=TaglinePage.choices,
        default=TaglinePage.ABOUT,
        db_index=True,
        unique=True,
        verbose_name=_('Page'),
        help_text=_('Inner page whose banner shows this tagline.'),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
        help_text=_('Reserved for admin list sorting.'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
    )
    text_az = models.TextField(
        validators=[MaxLengthValidator(400)],
        blank=True,
        verbose_name=_('Description (AZ)'),
    )
    text_en = models.TextField(
        validators=[MaxLengthValidator(400)],
        blank=True,
        verbose_name=_('Description (EN)'),
    )
    text_ru = models.TextField(
        validators=[MaxLengthValidator(400)],
        blank=True,
        verbose_name=_('Description (RU)'),
    )

    class Meta:
        verbose_name = _('Tagline')
        verbose_name_plural = _('Taglines')
        ordering = ('page', 'order', 'pk')

    def __str__(self):
        label = self.get_page_display()
        snippet = (self.text_az or self.text_en or self.text_ru or '').strip()
        if snippet:
            return f'{label} — {snippet[:60]}'
        return label

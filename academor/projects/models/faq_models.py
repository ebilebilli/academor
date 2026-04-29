from django.db import models


class SiteFaqEntry(models.Model):
    """About page FAQ (localized). Manage in admin under Site FAQ entries."""

    question_az = models.CharField('Question (AZ)', max_length=500)
    question_en = models.CharField('Question (EN)', max_length=500)
    question_ru = models.CharField('Question (RU)', max_length=500)

    answer_az = models.TextField('Answer (AZ)')
    answer_en = models.TextField('Answer (EN)')
    answer_ru = models.TextField('Answer (RU)')

    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Site FAQ entry'
        verbose_name_plural = 'Site FAQ entries'

    def __str__(self):
        return (self.question_az or self.question_en or self.question_ru or f'FAQ #{self.pk}')[:80]

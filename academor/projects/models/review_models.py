from django.db import models
from django.core.validators import MaxLengthValidator


class Review(models.Model):
    name = models.CharField(
        max_length=120,
        verbose_name='Name',
    )
    message = models.TextField(
        validators=[MaxLengthValidator(1000)],
        verbose_name='Review',
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Active',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

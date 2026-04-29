from django.core.validators import MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models


class Review(models.Model):
    name = models.CharField(
        max_length=120,
        verbose_name='Name',
    )
    message = models.TextField(
        validators=[MaxLengthValidator(1000)],
        verbose_name='Review',
    )
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        verbose_name='Rating (1–5)',
        help_text='Stars from 1 to 5.',
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

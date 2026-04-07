from django.db import models
from django.core.validators import MaxLengthValidator
from django.utils import timezone


class ContactInquiry(models.Model):
    full_name = models.CharField(
        null=True,
        blank=True,
        verbose_name='Full name'
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name='Email'
    )
    mobile_number = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name='Mobile number'
    )
    subject = models.CharField(
        null=True,
        blank=True,
        max_length=250,
        verbose_name='Subject'
    )
    info = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(500)],
        max_length=500,
        verbose_name='Additional info'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    created_date = models.DateField(
        default=timezone.now
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Read'
    )

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.created_date:
            self.created_date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Messages'

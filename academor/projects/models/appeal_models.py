import os
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.utils import timezone

from .vacancy_models import CareerOpening
from projects.utils import normalize_az_phone


class JobApplication(models.Model):
    vacancy = models.ForeignKey(
        CareerOpening,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appeal_set',
        verbose_name='Vacancy'
    )
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
    phone_number = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        verbose_name='Phone number'
    )
    info = models.CharField(
        null=True,
        blank=True,
        max_length=250,
        verbose_name='Additional info'
    )

    cv = models.FileField(
        upload_to='cvs/',  
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        verbose_name='CV'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Read'
    )

    class Meta:
        verbose_name = 'Job application'
        verbose_name_plural = 'Job applications'
        constraints = [
            models.UniqueConstraint(
                fields=['vacancy', 'email'],
                name='unique_email_per_vacancy'
            ),
            models.UniqueConstraint(
                fields=['vacancy', 'phone_number'],
                name='unique_phone_per_vacancy'
            ),
        ]
        ordering  = ['-created_at']

    def clean(self):
        if self.phone_number:
            normalized = normalize_az_phone(self.phone_number)
            if normalized:
                self.phone_number = normalized
            else:
                raise ValidationError({
                    'phone_number': 'Not a valid Azerbaijan mobile number.'
                })
        
    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)

    def __str__(self):
        return self.vacancy.title_az
    

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
            from django.utils import timezone
            self.created_date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Messages'
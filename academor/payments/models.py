from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    class ProductType(models.TextChoices):
        COURSE = 'course', _('Course')
        GENERIC = 'generic', _('Generic')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SUCCESS = 'success', _('Successful')
        CANCELLED = 'cancelled', _('Cancelled')
        DECLINED = 'declined', _('Declined')
        FAILED = 'failed', _('Failed')

    transaction_id = models.CharField(
        max_length=64, 
        unique=True, 
        db_index=True
    )
    client_order_id = models.CharField(
        max_length=64, 
        blank=True, 
        db_index=True
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2
    )
    currency = models.CharField(
        max_length=3, 
        default='AZN'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    description = models.CharField(
        max_length=255, 
        blank=True
    )
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.GENERIC,
        db_index=True,
    )
    course = models.ForeignKey(
        'projects.Service',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='payments',
        verbose_name=_('Course'),
    )
    price_package = models.ForeignKey(
        'projects.CoursePricePackage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='payments',
        verbose_name=_('Price package'),
    )
    buyer_email = models.EmailField(blank=True)
    buyer_name = models.CharField(max_length=255, blank=True)
    buyer_phone = models.CharField(max_length=30, blank=True)
    enrollment_completed_at = models.DateTimeField(null=True, blank=True)
    callback_up = models.TextField(
        blank=True
    )
    callback_payload = models.JSONField(
        default=dict, 
        blank=True
    )
    callback_received_at = models.DateTimeField(
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.transaction_id} — {self.amount} {self.currency} ({self.status})'


class CourseEnrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        CANCELLED = 'cancelled', _('Cancelled')

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='enrollment',
    )
    course = models.ForeignKey(
        'projects.Service',
        on_delete=models.PROTECT,
        related_name='enrollments',
    )
    price_package = models.ForeignKey(
        'projects.CoursePricePackage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='enrollments',
        verbose_name=_('Price package'),
    )
    buyer_email = models.EmailField(
        blank=True, 
        db_index=True
    )
    buyer_name = models.CharField(
        max_length=255, 
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    buyer_phone = models.CharField(max_length=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Course enrollment')
        verbose_name_plural = _('Course enrollments')

    def __str__(self):
        label = self.buyer_name or self.buyer_phone or self.buyer_email or '—'
        return f'{self.course_id} — {label} ({self.status})'

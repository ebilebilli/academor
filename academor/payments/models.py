from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Gözləyir'
        SUCCESS = 'success', 'Uğurlu'
        CANCELLED = 'cancelled', 'Ləğv'
        DECLINED = 'declined', 'Rədd'
        FAILED = 'failed', 'Uğursuz'

    transaction_id = models.CharField(max_length=64, unique=True, db_index=True)
    client_order_id = models.CharField(max_length=64, blank=True, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='AZN')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    description = models.CharField(max_length=255, blank=True)
    callback_up = models.TextField(blank=True)
    callback_payload = models.JSONField(default=dict, blank=True)
    callback_received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.transaction_id} — {self.amount} {self.currency} ({self.status})'

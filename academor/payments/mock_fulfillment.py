"""Fulfill mock test package purchases after successful payment."""

from __future__ import annotations

import logging

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from payments.models import Payment

logger = logging.getLogger('payments.mock')


def fulfill_mock_purchase(payment: Payment) -> bool:
    """Grant mock credits to the customer linked to a successful mock payment."""
    if payment.status != Payment.Status.SUCCESS:
        return False
    if payment.product_type != Payment.ProductType.MOCK_TEST:
        return False
    if not payment.customer_id or not payment.mock_package_id:
        return False
    if payment.enrollment_completed_at:
        return True

    package = payment.mock_package
    if not package or package.credits < 1:
        return False

    with transaction.atomic():
        locked = Payment.objects.select_for_update().filter(pk=payment.pk).first()
        if not locked or locked.enrollment_completed_at:
            return bool(locked and locked.enrollment_completed_at)

        from portals.models import CustomerProfile

        updated = CustomerProfile.objects.filter(pk=locked.customer_id).update(
            mock_credits=F('mock_credits') + package.credits,
        )
        if not updated:
            return False

        locked.enrollment_completed_at = timezone.now()
        locked.save(update_fields=['enrollment_completed_at', 'updated_at'])

    logger.info(
        'Mock purchase fulfilled payment_id=%s customer_id=%s package_id=%s credits=%s',
        payment.pk,
        payment.customer_id,
        package.pk,
        package.credits,
    )
    return True

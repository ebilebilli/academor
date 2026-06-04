"""Create course enrollment records after a successful payment."""

import logging

from django.db import transaction
from django.utils import timezone

from .models import CourseEnrollment, Payment

logger = logging.getLogger(__name__)


def fulfill_course_enrollment(payment: Payment) -> CourseEnrollment | None:
    """Create enrollment once when payment status is SUCCESS (idempotent)."""
    if payment.status != Payment.Status.SUCCESS:
        return None
    if not payment.course_id:
        return None

    existing = CourseEnrollment.objects.filter(payment=payment).first()
    if existing:
        return existing

    with transaction.atomic():
        locked = Payment.objects.select_for_update().filter(pk=payment.pk).first()
        if not locked or locked.status != Payment.Status.SUCCESS or not locked.course_id:
            return None
        if CourseEnrollment.objects.filter(payment=locked).exists():
            return CourseEnrollment.objects.get(payment=locked)

        enrollment = CourseEnrollment.objects.create(
            payment=locked,
            course_id=locked.course_id,
            price_package_id=locked.price_package_id,
            buyer_email=locked.buyer_email,
            buyer_name=locked.buyer_name,
            buyer_phone=locked.buyer_phone,
            status=CourseEnrollment.Status.ACTIVE,
        )
        if not locked.enrollment_completed_at:
            locked.enrollment_completed_at = timezone.now()
            locked.save(update_fields=['enrollment_completed_at', 'updated_at'])

        logger.info(
            'Course enrollment created payment_id=%s course_id=%s enrollment_id=%s',
            locked.pk,
            locked.course_id,
            enrollment.pk,
        )
        return enrollment

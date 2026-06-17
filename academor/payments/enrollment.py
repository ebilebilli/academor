"""Create course enrollment records after a successful payment."""

import logging

from django.db import transaction
from django.utils import timezone

from .contract import generate_contract_number, render_course_contract_html
from .models import CourseEnrollment, Payment

logger = logging.getLogger(__name__)


def _persist_enrollment_contract(enrollment: CourseEnrollment, payment: Payment) -> None:
    contract_number = (payment.contract_number or '').strip() or generate_contract_number()
    if not payment.contract_number:
        payment.contract_number = contract_number
        payment.save(update_fields=['contract_number', 'updated_at'])

    contract_html = render_course_contract_html(
        course=enrollment.course,
        package=enrollment.price_package,
        contract_number=contract_number,
        buyer_name=enrollment.buyer_name,
        buyer_phone=enrollment.buyer_phone,
        contract_date=timezone.localtime(payment.created_at).date(),
        lang=(payment.contract_language or 'az')[:2],
    )
    enrollment.contract_number = contract_number
    enrollment.contract_html = contract_html
    enrollment.save(update_fields=['contract_number', 'contract_html'])


def fulfill_course_enrollment(payment: Payment) -> CourseEnrollment | None:
    """Create enrollment once when payment status is SUCCESS (idempotent)."""
    if payment.status != Payment.Status.SUCCESS:
        return None
    if not payment.course_id:
        return None

    existing = (
        CourseEnrollment.objects.select_related('course', 'price_package')
        .filter(payment=payment)
        .first()
    )
    if existing:
        if not existing.contract_html:
            _persist_enrollment_contract(existing, payment)
        return existing

    with transaction.atomic():
        locked = Payment.objects.select_for_update().filter(pk=payment.pk).first()
        if not locked or locked.status != Payment.Status.SUCCESS or not locked.course_id:
            return None
        if CourseEnrollment.objects.filter(payment=locked).exists():
            enrollment = (
                CourseEnrollment.objects.select_related('course', 'price_package')
                .get(payment=locked)
            )
            if not enrollment.contract_html:
                _persist_enrollment_contract(enrollment, locked)
            return enrollment

        enrollment = CourseEnrollment.objects.create(
            payment=locked,
            course_id=locked.course_id,
            price_package_id=locked.price_package_id,
            buyer_email=locked.buyer_email,
            buyer_name=locked.buyer_name,
            buyer_phone=locked.buyer_phone,
            status=CourseEnrollment.Status.ACTIVE,
        )
        enrollment = (
            CourseEnrollment.objects.select_related('course', 'price_package')
            .get(pk=enrollment.pk)
        )
        _persist_enrollment_contract(enrollment, locked)

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

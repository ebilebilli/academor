"""Fulfill mock test package purchases after successful payment."""

from __future__ import annotations

import logging

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from payments.contract import generate_contract_number
from payments.mock_contract import render_mock_contract_html
from payments.models import CourseEnrollment, Payment

logger = logging.getLogger('payments.mock')


def _mock_credits_for_payment(payment: Payment) -> int | None:
    if payment.price_package_id and payment.price_package:
        credits = payment.price_package.credits
        return credits if credits and credits >= 1 else None
    return None


def _contract_package_for_payment(payment: Payment):
    if payment.price_package_id and payment.price_package:
        return payment.price_package
    return None


def _persist_mock_enrollment_contract(
    enrollment: CourseEnrollment,
    payment: Payment,
) -> None:
    contract_number = (payment.contract_number or '').strip() or generate_contract_number()
    if not payment.contract_number:
        payment.contract_number = contract_number
        payment.save(update_fields=['contract_number', 'updated_at'])

    package = _contract_package_for_payment(payment)
    if not package:
        return

    contract_html = render_mock_contract_html(
        package=package,
        contract_number=contract_number,
        buyer_name=enrollment.buyer_name,
        buyer_phone=enrollment.buyer_phone,
        contract_date=timezone.localtime(payment.created_at).date(),
        lang=(payment.contract_language or 'az')[:2],
    )
    enrollment.contract_number = contract_number
    enrollment.contract_html = contract_html
    enrollment.save(update_fields=['contract_number', 'contract_html'])


def _mock_credit_field_for_course(course) -> str | None:
    if not course:
        return None
    if course.ielts_mock_test:
        return 'ielts_mock_credits'
    if course.sat_mock_test:
        return 'sat_mock_credits'
    return None


def fulfill_mock_purchase(payment: Payment) -> bool:
    """Grant mock credits and create an enrollment record after successful payment."""
    if payment.status != Payment.Status.SUCCESS:
        return False
    if payment.product_type != Payment.ProductType.MOCK_TEST:
        return False
    if not payment.customer_id:
        return False
    credits = _mock_credits_for_payment(payment)
    if not credits:
        return False
    if payment.enrollment_completed_at:
        return True

    credit_field = None
    with transaction.atomic():
        locked = Payment.objects.select_for_update().filter(pk=payment.pk).first()
        if not locked or locked.enrollment_completed_at:
            return bool(locked and locked.enrollment_completed_at)

        locked_credits = _mock_credits_for_payment(locked)
        if not locked_credits:
            return False

        credit_field = _mock_credit_field_for_course(locked.course)
        if not credit_field:
            logger.error(
                'Mock purchase missing program flag payment_id=%s course_id=%s',
                locked.pk,
                locked.course_id,
            )
            return False

        from portals.models import CustomerProfile

        updated = CustomerProfile.objects.filter(pk=locked.customer_id).update(
            **{credit_field: F(credit_field) + locked_credits},
        )
        if not updated:
            return False

        enrollment = (
            CourseEnrollment.objects.select_related('price_package', 'customer')
            .filter(payment=locked)
            .first()
        )
        if not enrollment:
            enrollment = CourseEnrollment.objects.create(
                payment=locked,
                course_id=locked.course_id,
                price_package_id=locked.price_package_id,
                customer_id=locked.customer_id,
                buyer_email=locked.buyer_email,
                buyer_name=locked.buyer_name,
                buyer_phone=locked.buyer_phone,
                status=CourseEnrollment.Status.ACTIVE,
            )
            enrollment = (
                CourseEnrollment.objects.select_related(
                    'price_package',
                    'customer',
                )
                .get(pk=enrollment.pk)
            )

        if not enrollment.contract_html:
            _persist_mock_enrollment_contract(enrollment, locked)

        locked.enrollment_completed_at = timezone.now()
        locked.save(update_fields=['enrollment_completed_at', 'updated_at'])

    logger.info(
        'Mock purchase fulfilled payment_id=%s customer_id=%s credits=%s field=%s',
        payment.pk,
        payment.customer_id,
        credits,
        credit_field,
    )
    return True

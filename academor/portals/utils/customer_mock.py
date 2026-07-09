"""Customer mock test credit and session helpers."""

from __future__ import annotations

from django.db import transaction
from django.db.models import F
from django.urls import reverse
from django.utils.translation import gettext as _

from portals.models import CustomerProfile, IeltsMockTestAttempt, Quiz
from portals.utils.ielts_mock_test import (
    IELTS_SERVICE,
    SECTION_SPECS,
    _content_filter_for_section,
    advance_mock_after_section_submit,
    serialize_mock_attempt_summary,
    serialize_mock_progress,
    validate_mock_section_submit,
)


def customer_has_in_progress_mock(customer_id: int) -> bool:
    return IeltsMockTestAttempt.objects.filter(
        customer_id=customer_id,
        status=IeltsMockTestAttempt.Status.IN_PROGRESS,
    ).exists()


def customer_can_start_mock(customer_id: int) -> bool:
    profile = CustomerProfile.objects.filter(pk=customer_id).first()
    if not profile:
        return False
    if customer_has_in_progress_mock(customer_id):
        return True
    return profile.mock_credits > 0


def _eligible_quizzes_for_customer_section(section: str, flag_kwargs: dict):
    qs = (
        Quiz.objects.filter(
            category__service=IELTS_SERVICE,
            **flag_kwargs,
        )
        .annotate(has_content=_content_filter_for_section(section))
        .filter(has_content=True)
        .select_related('category')
    )
    return list(qs)


def pick_random_customer_section_quizzes() -> dict[str, Quiz | None]:
    import random

    picked: dict[str, Quiz | None] = {}
    for section, flag_kwargs in SECTION_SPECS:
        candidates = _eligible_quizzes_for_customer_section(section, flag_kwargs)
        picked[section] = random.choice(candidates) if candidates else None
    return picked


def get_missing_customer_mock_sections() -> list[str]:
    picked = pick_random_customer_section_quizzes()
    return [section for section, quiz in picked.items() if quiz is None]


def abandon_in_progress_customer_mock_attempts(customer_id: int) -> None:
    IeltsMockTestAttempt.objects.filter(
        customer_id=customer_id,
        status=IeltsMockTestAttempt.Status.IN_PROGRESS,
    ).update(status=IeltsMockTestAttempt.Status.ABANDONED)


@transaction.atomic
def start_customer_mock_test_attempt(customer_id: int) -> tuple[IeltsMockTestAttempt | None, str | None]:
    profile = CustomerProfile.objects.select_for_update().filter(pk=customer_id).first()
    if not profile:
        return None, str(_('Customer profile not found.'))

    if customer_has_in_progress_mock(customer_id):
        abandon_in_progress_customer_mock_attempts(customer_id)

    if profile.mock_credits < 1:
        return None, str(_('You have no mock test credits. Purchase a package to continue.'))

    picked = pick_random_customer_section_quizzes()
    missing = [section for section, quiz in picked.items() if quiz is None]
    if missing:
        labels = ', '.join(
            str(dict(IeltsMockTestAttempt.Section.choices).get(section, section))
            for section in missing
        )
        return None, str(_('Not enough quizzes are available for: %(sections)s.') % {'sections': labels})

    attempt = IeltsMockTestAttempt.objects.create(
        customer_id=customer_id,
        status=IeltsMockTestAttempt.Status.IN_PROGRESS,
        current_section=IeltsMockTestAttempt.Section.LISTENING,
        listening_quiz=picked[IeltsMockTestAttempt.Section.LISTENING],
        reading_quiz=picked[IeltsMockTestAttempt.Section.READING],
        writing_quiz=picked[IeltsMockTestAttempt.Section.WRITING],
        speaking_quiz=picked[IeltsMockTestAttempt.Section.SPEAKING],
    )
    return attempt, None


@transaction.atomic
def consume_customer_mock_credit_on_quiz_start(
    customer_id: int,
    attempt_id: int,
    quiz_id: int,
) -> tuple[bool, str | None]:
    """Deduct one credit when the customer starts the first Listening quiz."""
    from portals.utils.ielts_mock_test import section_for_quiz_in_attempt

    attempt = (
        IeltsMockTestAttempt.objects.select_for_update()
        .filter(
            pk=attempt_id,
            customer_id=customer_id,
            status=IeltsMockTestAttempt.Status.IN_PROGRESS,
        )
        .first()
    )
    if not attempt:
        return False, str(_('Mock test session is no longer active.'))

    if attempt.credit_consumed:
        return True, None

    section = section_for_quiz_in_attempt(attempt, quiz_id)
    if section != IeltsMockTestAttempt.Section.LISTENING:
        return False, str(_('Mock test credit must be applied before starting the first section.'))

    profile = CustomerProfile.objects.select_for_update().filter(pk=customer_id).first()
    if not profile or profile.mock_credits < 1:
        return False, str(_('You have no mock test credits. Purchase a package to continue.'))

    CustomerProfile.objects.filter(pk=customer_id).update(mock_credits=F('mock_credits') - 1)
    attempt.credit_consumed = True
    attempt.save(update_fields=['credit_consumed'])
    return True, None


def get_mock_attempt_for_customer(customer_id: int, attempt_id: int) -> IeltsMockTestAttempt | None:
    return (
        IeltsMockTestAttempt.objects.filter(
            pk=attempt_id,
            customer_id=customer_id,
        )
        .select_related(
            'listening_quiz__category',
            'reading_quiz__category',
            'writing_quiz__category',
            'speaking_quiz__category',
            'listening_result',
            'reading_result',
            'writing_result',
            'speaking_result',
            'customer__user',
        )
        .first()
    )


def get_active_customer_mock_attempt(customer_id: int, attempt_id: int) -> IeltsMockTestAttempt | None:
    attempt = get_mock_attempt_for_customer(customer_id, attempt_id)
    if not attempt or attempt.status != IeltsMockTestAttempt.Status.IN_PROGRESS:
        return None
    return attempt


def abandon_customer_mock_test_attempt(customer_id: int, attempt_id: int) -> None:
    IeltsMockTestAttempt.objects.filter(
        pk=attempt_id,
        customer_id=customer_id,
        status=IeltsMockTestAttempt.Status.IN_PROGRESS,
    ).update(status=IeltsMockTestAttempt.Status.ABANDONED)


def get_customer_completed_mock_attempts(customer_id: int, *, limit: int = 20):
    return (
        IeltsMockTestAttempt.objects.filter(
            customer_id=customer_id,
            status=IeltsMockTestAttempt.Status.COMPLETED,
        )
        .select_related(
            'customer__user',
            'listening_quiz__category',
            'reading_quiz__category',
            'writing_quiz__category',
            'speaking_quiz__category',
            'listening_result',
            'reading_result',
            'writing_result',
            'speaking_result',
        )
        .order_by('-completed_at', '-id')[:limit]
    )


def get_customer_mock_take_url(attempt: IeltsMockTestAttempt, section: str) -> str:
    """Customer mock take URLs (parallel to student routes)."""
    quiz = attempt.quiz_for_section(section)
    if not quiz:
        return reverse('portals:customer-ielts-mock')

    if section == IeltsMockTestAttempt.Section.LISTENING:
        url_name = 'portals:customer-manual-quiz-take'
    elif section == IeltsMockTestAttempt.Section.READING:
        url_name = 'portals:customer-reading-quiz-take'
    elif section == IeltsMockTestAttempt.Section.WRITING:
        url_name = 'portals:customer-manual-quiz-take'
    elif section == IeltsMockTestAttempt.Section.SPEAKING:
        url_name = 'portals:customer-speaking-quiz-take'
    else:
        return reverse('portals:customer-ielts-mock')

    base = reverse(url_name, kwargs={'pk': quiz.pk})
    return f'{base}?mock={attempt.pk}'


def get_customer_mock_current_take_url(attempt: IeltsMockTestAttempt) -> str:
    return get_customer_mock_take_url(attempt, attempt.current_section)


def resolve_customer_mock_take_request(
    customer_id: int,
    mock_id: int | None,
    quiz_id: int,
) -> dict:
    if not mock_id:
        return {}

    attempt = get_mock_attempt_for_customer(customer_id, mock_id)
    if not attempt:
        return {'mock_redirect': reverse('portals:customer-ielts-mock')}

    if attempt.status == IeltsMockTestAttempt.Status.COMPLETED:
        return {
            'mock_redirect': reverse(
                'portals:customer-ielts-mock-complete',
                kwargs={'pk': attempt.pk},
            ),
        }

    if attempt.status != IeltsMockTestAttempt.Status.IN_PROGRESS:
        return {'mock_redirect': reverse('portals:customer-ielts-mock')}

    from portals.utils.ielts_mock_test import section_for_quiz_in_attempt

    section = section_for_quiz_in_attempt(attempt, quiz_id)
    if not section or section != attempt.current_section:
        return {'mock_redirect': get_customer_mock_current_take_url(attempt)}

    return {
        'mock_attempt': serialize_mock_progress(attempt),
        'mock_id': attempt.pk,
        'back_url': reverse('portals:customer-ielts-mock'),
    }


def resolve_customer_mock_start_request(
    customer_id: int,
    mock_id: int | None,
    quiz_id: int,
) -> dict | None:
    if not mock_id:
        return None

    attempt = get_active_customer_mock_attempt(customer_id, mock_id)
    if not attempt:
        return {
            'success': False,
            'error': str(_('Mock test session is no longer active.')),
        }

    validation_error = validate_mock_section_submit(attempt, quiz_id)
    if validation_error:
        return {
            'success': True,
            'redirect_url': get_customer_mock_current_take_url(attempt),
        }

    return None


def customer_mock_allows_active_section_take(
    customer_id: int,
    mock_attempt_id: int | None,
    quiz_id: int,
) -> bool:
    if not mock_attempt_id:
        return False
    attempt = get_active_customer_mock_attempt(customer_id, mock_attempt_id)
    if not attempt:
        return False
    from portals.utils.ielts_mock_test import section_for_quiz_in_attempt

    section = section_for_quiz_in_attempt(attempt, quiz_id)
    if not section or section != attempt.current_section:
        return False
    return attempt.result_for_section(section) is None


def apply_customer_mock_submit_result(
    *,
    customer_id: int,
    mock_attempt_id: int | None,
    quiz_id: int,
    result,
    response: dict,
) -> dict:
    if not mock_attempt_id:
        return response

    attempt = get_active_customer_mock_attempt(customer_id, mock_attempt_id)
    if not attempt:
        response['mock_error'] = str(_('Mock test session is no longer active.'))
        return response

    validation_error = validate_mock_section_submit(attempt, quiz_id)
    if validation_error:
        response['success'] = False
        response['error'] = validation_error
        response['redirect_url'] = get_customer_mock_current_take_url(attempt)
        return response

    from portals.utils.ielts_mock_test import (
        NEXT_SECTION_BY_SECTION,
        section_for_quiz_in_attempt,
    )

    section = section_for_quiz_in_attempt(attempt, quiz_id)
    if not section:
        response['success'] = False
        response['error'] = str(_('Invalid mock test section.'))
        return response

    attempt = advance_mock_after_section_submit(attempt, section=section, result=result)
    next_section = NEXT_SECTION_BY_SECTION.get(section)
    section_labels = dict(IeltsMockTestAttempt.Section.choices)
    completed_label = section_labels.get(section, section)
    response['next_url'] = (
        get_customer_mock_take_url(attempt, next_section)
        if next_section
        else reverse('portals:customer-ielts-mock-complete', kwargs={'pk': attempt.pk})
    )
    response['mock_attempt_id'] = attempt.pk
    response['mock_continue'] = True
    response['mock_completed'] = attempt.status == IeltsMockTestAttempt.Status.COMPLETED
    response['mock_section_completed'] = section
    response['mock_section_completed_label'] = str(completed_label)
    if next_section:
        next_label = section_labels.get(next_section, next_section)
        response['mock_next_section'] = next_section
        response['mock_next_section_label'] = str(next_label)
        response['mock_continue_message'] = str(
            _('%(completed)s is done. Next: %(next)s.') % {
                'completed': completed_label,
                'next': next_label,
            }
        )
    else:
        response['mock_continue_message'] = str(
            _('%(completed)s is done. Your mock test is complete.') % {
                'completed': completed_label,
            }
        )

    if attempt.status == IeltsMockTestAttempt.Status.COMPLETED:
        from portals.utils.notifications import (
            create_mock_section_review_notifications,
            create_mock_test_completed_notifications,
        )
        from portals.utils.ielts_mock_test import MANUAL_SECTIONS

        if section in MANUAL_SECTIONS:
            create_mock_section_review_notifications(attempt, result, section)
        create_mock_test_completed_notifications(attempt)

    return response


def serialize_customer_mock_attempt_summary(attempt: IeltsMockTestAttempt) -> dict:
    data = serialize_mock_attempt_summary(attempt)
    if attempt.customer_id:
        data['student_name'] = attempt.customer.full_name
    return data


def get_active_mock_packages():
    from portals.models import MockTestPackage

    return MockTestPackage.objects.filter(is_active=True, price__gt=0, credits__gt=0).order_by('order', 'id')

"""Customer mock test credit and session helpers."""

from __future__ import annotations

from django.db import transaction
from django.db.models import F
from django.urls import reverse
from django.utils.translation import gettext as _

from portals.models import CustomerProfile, IeltsMockTestAttempt, Quiz
from projects.models import MOCK_TEST_SERVICE_Q
from portals.utils.ielts_mock_test import (
    IELTS_SERVICE,
    SAT_SERVICE,
    _attempt_create_kwargs,
    advance_mock_after_section_submit,
    get_mock_complete_url,
    get_mock_landing_url,
    get_mock_take_url,
    pick_random_customer_section_quizzes,
    serialize_mock_attempt_summary,
    serialize_mock_progress,
    validate_mock_section_submit,
)
from portals.utils.mock_programs import (
    MOCK_EXAM_PROGRAMS,
    get_manual_sections,
    get_next_section,
    get_program_first_section,
    get_program_label,
    get_section_label,
    is_valid_mock_program,
)


def _mock_credit_field_for_program(exam_program: str) -> str | None:
    if exam_program == IELTS_SERVICE:
        return 'ielts_mock_credits'
    if exam_program == SAT_SERVICE:
        return 'sat_mock_credits'
    return None


def _customer_in_progress_program(customer_id: int) -> str | None:
    return (
        IeltsMockTestAttempt.objects.filter(
            customer_id=customer_id,
            status=IeltsMockTestAttempt.Status.IN_PROGRESS,
        )
        .values_list('exam_program', flat=True)
        .first()
    )


def customer_can_view_mock_program(customer_id: int, exam_program: str) -> bool:
    if not is_valid_mock_program(exam_program):
        return False
    if exam_program in get_customer_mock_exam_programs(customer_id):
        return True
    return IeltsMockTestAttempt.objects.filter(
        customer_id=customer_id,
        exam_program=exam_program,
        status=IeltsMockTestAttempt.Status.COMPLETED,
    ).exists()


def build_customer_mock_dashboard_sections(customer_id: int) -> list[dict]:
    """One dashboard action block per visible mock program (IELTS, SAT, …)."""
    profile = CustomerProfile.objects.filter(pk=customer_id).first()
    if not profile:
        return []

    sections = []
    for program in MOCK_EXAM_PROGRAMS:
        if not customer_can_view_mock_program(customer_id, program):
            continue
        sections.append({
            'program': program,
            'label': get_program_label(program),
            'credits': profile.mock_credits_for_program(program),
            'in_progress': customer_has_in_progress_mock(customer_id, exam_program=program),
            'can_start': customer_can_start_mock(customer_id, program),
            'landing_url': reverse('portals:customer-mock-landing', kwargs={'program': program}),
        })
    return sections


def get_customer_selectable_mock_programs(customer_id: int) -> list[str]:
    """Programs a customer may pick on the mock chooser (credits, in-progress, or history)."""
    return [
        program for program in MOCK_EXAM_PROGRAMS
        if customer_can_view_mock_program(customer_id, program)
    ]


def build_customer_mock_picker_programs(customer_id: int) -> list[dict]:
    from django.db.models import Count

    profile = CustomerProfile.objects.filter(pk=customer_id).first()
    if not profile:
        return []

    programs = get_customer_selectable_mock_programs(customer_id)
    if not programs:
        return []

    in_progress_programs = set(
        IeltsMockTestAttempt.objects.filter(
            customer_id=customer_id,
            status=IeltsMockTestAttempt.Status.IN_PROGRESS,
            exam_program__in=programs,
        ).values_list('exam_program', flat=True)
    )
    completed_counts = dict(
        IeltsMockTestAttempt.objects.filter(
            customer_id=customer_id,
            exam_program__in=programs,
            status=IeltsMockTestAttempt.Status.COMPLETED,
        )
        .values('exam_program')
        .annotate(c=Count('id'))
        .values_list('exam_program', 'c')
    )

    cards = []
    for program in programs:
        cards.append({
            'code': program,
            'label': get_program_label(program),
            'landing_url': reverse('portals:customer-mock-landing', kwargs={'program': program}),
            'credits': profile.mock_credits_for_program(program),
            'in_progress': program in in_progress_programs,
            'can_start': customer_can_start_mock(customer_id, program),
            'completed_count': int(completed_counts.get(program, 0)),
        })
    return cards


def get_customer_mock_exam_programs(customer_id: int) -> list[str]:
    profile = CustomerProfile.objects.filter(pk=customer_id).first()
    if not profile:
        return []

    programs: list[str] = []
    in_progress = _customer_in_progress_program(customer_id)
    if in_progress and is_valid_mock_program(in_progress):
        programs.append(in_progress)

    if profile.ielts_mock_credits > 0 and IELTS_SERVICE not in programs:
        programs.append(IELTS_SERVICE)
    if profile.sat_mock_credits > 0 and SAT_SERVICE not in programs:
        programs.append(SAT_SERVICE)
    return programs


def resolve_customer_mock_exam_program(
    customer_id: int,
    preferred: str | None = None,
) -> str | None:
    programs = get_customer_mock_exam_programs(customer_id)
    if not programs:
        return None
    if preferred and preferred in programs:
        return preferred
    if len(programs) == 1:
        return programs[0]
    return None


def customer_has_in_progress_mock(customer_id: int, *, exam_program: str | None = None) -> bool:
    qs = IeltsMockTestAttempt.objects.filter(
        customer_id=customer_id,
        status=IeltsMockTestAttempt.Status.IN_PROGRESS,
    )
    if exam_program:
        qs = qs.filter(exam_program=exam_program)
    return qs.exists()


def customer_can_start_mock(customer_id: int, exam_program: str | None = None) -> bool:
    profile = CustomerProfile.objects.filter(pk=customer_id).first()
    if not profile:
        return False
    if exam_program:
        if customer_has_in_progress_mock(customer_id, exam_program=exam_program):
            return True
        return profile.mock_credits_for_program(exam_program) > 0
    if customer_has_in_progress_mock(customer_id):
        return True
    return profile.mock_credits > 0


def get_missing_customer_mock_sections(*, exam_program: str = IELTS_SERVICE) -> list[str]:
    picked = pick_random_customer_section_quizzes(exam_program=exam_program)
    return [section for section, quiz in picked.items() if quiz is None]


def abandon_in_progress_customer_mock_attempts(
    customer_id: int,
    *,
    exam_program: str | None = None,
) -> None:
    qs = IeltsMockTestAttempt.objects.filter(
        customer_id=customer_id,
        status=IeltsMockTestAttempt.Status.IN_PROGRESS,
    )
    if exam_program:
        qs = qs.filter(exam_program=exam_program)
    qs.update(status=IeltsMockTestAttempt.Status.ABANDONED)


@transaction.atomic
def start_customer_mock_test_attempt(
    customer_id: int,
    exam_program: str,
) -> tuple[IeltsMockTestAttempt | None, str | None]:
    if not is_valid_mock_program(exam_program):
        return None, str(_('Unknown mock test program.'))

    profile = CustomerProfile.objects.select_for_update().filter(pk=customer_id).first()
    if not profile:
        return None, str(_('Customer profile not found.'))

    if customer_has_in_progress_mock(customer_id):
        abandon_in_progress_customer_mock_attempts(customer_id)

    credit_field = _mock_credit_field_for_program(exam_program)
    if not credit_field or profile.mock_credits_for_program(exam_program) < 1:
        return None, str(_('You have no mock test credits. Purchase a package to continue.'))

    picked = pick_random_customer_section_quizzes(exam_program=exam_program)
    missing = [section for section, quiz in picked.items() if quiz is None]
    if missing:
        labels = ', '.join(
            get_section_label(exam_program, section)
            for section in missing
        )
        return None, str(_('Not enough quizzes are available for: %(sections)s.') % {'sections': labels})

    attempt = IeltsMockTestAttempt.objects.create(
        customer_id=customer_id,
        **_attempt_create_kwargs(exam_program, picked),
    )
    return attempt, None


@transaction.atomic
def consume_customer_mock_credit_on_quiz_start(
    customer_id: int,
    attempt_id: int,
    quiz_id: int,
) -> tuple[bool, str | None]:
    """Deduct one credit when the customer starts the first mock section."""
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
    first_section = get_program_first_section(attempt.exam_program)
    if section != first_section:
        return False, str(_('Mock test credit must be applied before starting the first section.'))

    credit_field = _mock_credit_field_for_program(attempt.exam_program)
    profile = CustomerProfile.objects.select_for_update().filter(pk=customer_id).first()
    if not profile or not credit_field or profile.mock_credits_for_program(attempt.exam_program) < 1:
        return False, str(_('You have no mock test credits. Purchase a package to continue.'))

    CustomerProfile.objects.filter(pk=customer_id).update(**{credit_field: F(credit_field) - 1})
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
            'math_quiz__category',
            'listening_result',
            'reading_result',
            'writing_result',
            'speaking_result',
            'math_result',
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


def get_customer_completed_mock_attempts(
    customer_id: int,
    *,
    exam_program: str | None = None,
    limit: int = 20,
):
    qs = IeltsMockTestAttempt.objects.filter(
        customer_id=customer_id,
        status=IeltsMockTestAttempt.Status.COMPLETED,
    )
    if exam_program:
        qs = qs.filter(exam_program=exam_program)
    return (
        qs.select_related(
            'customer__user',
            'listening_quiz__category',
            'reading_quiz__category',
            'writing_quiz__category',
            'speaking_quiz__category',
            'math_quiz__category',
            'listening_result',
            'reading_result',
            'writing_result',
            'speaking_result',
            'math_result',
        )
        .order_by('-completed_at', '-id')[:limit]
    )


def get_customer_mock_take_url(attempt: IeltsMockTestAttempt, section: str) -> str:
    return get_mock_take_url(attempt, section, role='customer')


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
        programs = get_customer_mock_exam_programs(customer_id)
        program = programs[0] if len(programs) == 1 else IELTS_SERVICE
        return {'mock_redirect': get_mock_landing_url(program, role='customer')}

    if attempt.status == IeltsMockTestAttempt.Status.COMPLETED:
        return {'mock_redirect': get_mock_complete_url(attempt, role='customer')}

    if attempt.status != IeltsMockTestAttempt.Status.IN_PROGRESS:
        return {'mock_redirect': get_mock_landing_url(attempt.exam_program, role='customer')}

    from portals.utils.ielts_mock_test import section_for_quiz_in_attempt

    section = section_for_quiz_in_attempt(attempt, quiz_id)
    if not section or section != attempt.current_section:
        return {'mock_redirect': get_customer_mock_current_take_url(attempt)}

    return {
        'mock_attempt': serialize_mock_progress(attempt),
        'mock_id': attempt.pk,
        'back_url': get_mock_landing_url(attempt.exam_program, role='customer'),
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

    from portals.utils.ielts_mock_test import section_for_quiz_in_attempt

    section = section_for_quiz_in_attempt(attempt, quiz_id)
    if not section:
        response['success'] = False
        response['error'] = str(_('Invalid mock test section.'))
        return response

    attempt = advance_mock_after_section_submit(attempt, section=section, result=result)
    next_section = get_next_section(attempt.exam_program, section)
    completed_label = get_section_label(attempt.exam_program, section)
    response['next_url'] = (
        get_customer_mock_take_url(attempt, next_section)
        if next_section
        else get_mock_complete_url(attempt, role='customer')
    )
    response['mock_attempt_id'] = attempt.pk
    response['mock_continue'] = True
    response['mock_completed'] = attempt.status == IeltsMockTestAttempt.Status.COMPLETED
    response['mock_section_completed'] = section
    response['mock_section_completed_label'] = str(completed_label)
    if next_section:
        next_label = get_section_label(attempt.exam_program, next_section)
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

        if section in get_manual_sections(attempt.exam_program):
            create_mock_section_review_notifications(attempt, result, section)
        create_mock_test_completed_notifications(attempt)

    return response


def serialize_customer_mock_attempt_summary(attempt: IeltsMockTestAttempt) -> dict:
    data = serialize_mock_attempt_summary(attempt)
    if attempt.customer_id:
        data['student_name'] = attempt.customer.full_name
    return data


def get_active_mock_packages_services():
    from projects.models import Service

    return (
        Service.objects.filter(is_active=True)
        .filter(MOCK_TEST_SERVICE_Q)
        .prefetch_related('price_packages')
        .order_by('order', 'id')
    )


def get_customer_mock_home_url(customer_id: int) -> str:
    programs = get_customer_selectable_mock_programs(customer_id)
    if len(programs) == 1:
        return reverse('portals:customer-mock-landing', kwargs={'program': programs[0]})
    if programs:
        return reverse('portals:customer-mock-picker')
    return reverse('portals:customer-mock-packages')

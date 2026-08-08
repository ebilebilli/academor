"""Portal mock test session helpers."""

from __future__ import annotations

import logging
import math
import random

from django.db import transaction
from django.db.models import Exists, OuterRef, Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from portals.models import (
    IeltsMockTestAttempt,
    ListeningQuestion,
    Quiz,
    QuizQuestion,
    QuizResult,
    ReadingQuestion,
    SpeakingQuestion,
)
from portals.utils.mock_programs import (
    IELTS_BAND_MAX,
    IELTS_SERVICE,
    MOCK_EXAM_PROGRAMS,
    PROGRAM_LABELS,
    SAT_SECTION_SCORE_MAX,
    SAT_SECTION_SCORE_MIN,
    SAT_SERVICE,
    SAT_TOTAL_SCORE_MAX,
    get_auto_sections,
    get_inter_section_rest_seconds,
    get_manual_sections,
    get_next_section,
    get_program_first_section,
    get_program_label,
    get_program_quiz_filters,
    get_program_scoring_mode,
    get_program_sections,
    get_section_label,
    get_section_order,
    get_section_spec,
    get_take_url_name,
    is_final_section,
    is_valid_mock_program,
    resolve_take_url_kind,
    sat_section_scaled_score,
    section_index_for_program,
)
from portals.utils.quiz_assignments import student_has_active_mock_access_for_program
from portals.utils.student_courses import get_student_course_type_codes, student_has_course_access

# Backward-compatible aliases for existing imports.
MockTestAttempt = IeltsMockTestAttempt
PROGRAM_QUIZ_FLAG_FIELD = {
    IELTS_SERVICE: 'is_ielts',
    SAT_SERVICE: 'is_sat',
}

logger = logging.getLogger('portals.mock_test')


def get_student_mock_exam_programs(student_id: int) -> list[str]:
    codes = set(get_student_course_type_codes(student_id))
    programs: list[str] = []
    if IELTS_SERVICE in codes:
        programs.append(IELTS_SERVICE)
    if SAT_SERVICE in codes:
        programs.append(SAT_SERVICE)
    return programs


def resolve_student_mock_exam_program(
    student_id: int,
    preferred: str | None = None,
) -> str | None:
    """Return the active mock program for a student, optionally pinned by URL."""
    programs = get_student_mock_exam_programs(student_id)
    if not programs:
        return None
    if preferred and preferred in programs:
        return preferred
    if len(programs) == 1:
        return programs[0]
    return None


def student_can_access_mock(student_id: int) -> bool:
    """True when at least one enrolled mock program is unlocked."""
    from portals.utils.quiz_assignments import student_has_active_mock_access

    return student_has_active_mock_access(student_id)


def student_can_access_mock_program(student_id: int, exam_program: str) -> bool:
    """Teacher must activate mock access for the enrolled program."""
    return student_has_active_mock_access_for_program(student_id, exam_program)


def student_can_access_ielts_mock(student_id: int) -> bool:
    return student_can_access_mock_program(student_id, IELTS_SERVICE)


def _program_quiz_filters(exam_program: str) -> dict:
    return get_program_quiz_filters(exam_program)


def _listening_quiz_has_content():
    return Exists(
        ListeningQuestion.objects.filter(audio__quiz_id=OuterRef('pk')),
    )


def _reading_quiz_has_content():
    return Exists(
        ReadingQuestion.objects.filter(passage__quiz_id=OuterRef('pk')),
    )


def _essay_quiz_has_content():
    return Exists(
        QuizQuestion.objects.filter(quiz_id=OuterRef('pk')).exclude(
            Q(question='') & Q(prompt_type='text'),
        ),
    )


def _speaking_quiz_has_content():
    return Exists(
        SpeakingQuestion.objects.filter(part__quiz_id=OuterRef('pk')),
    )


def _sat_mock_quiz_has_content():
    variant = Q(
        is_reading=False,
        is_math=False,
        is_listening=False,
        is_essay=False,
        is_speaking=False,
    )
    return (
        (Q(is_reading=True) & _reading_quiz_has_content())
        | (variant & _essay_quiz_has_content())
    )


def _content_filter_for_section(section_key: str, exam_program: str):
    spec = get_section_spec(exam_program, section_key)
    if not spec:
        return Q(pk__in=[])
    if not spec.quiz_flags and spec.sat_sections:
        return _sat_mock_quiz_has_content()
    if not spec.quiz_flags:
        return _essay_quiz_has_content()
    if 'is_listening' in spec.quiz_flags:
        return _listening_quiz_has_content()
    if 'is_reading' in spec.quiz_flags:
        return _reading_quiz_has_content()
    if 'is_math' in spec.quiz_flags:
        return _reading_quiz_has_content()
    if 'is_essay' in spec.quiz_flags:
        return _essay_quiz_has_content()
    if 'is_speaking' in spec.quiz_flags:
        return _speaking_quiz_has_content()
    return Q(pk__in=[])


def standalone_quiz_results(**filters):
    """Quiz results from normal (non-mock) attempts only."""
    return QuizResult.objects.filter(ielts_mock_attempt__isnull=True, **filters)


def is_mock_quiz_result(result: QuizResult | None) -> bool:
    return bool(result and getattr(result, 'ielts_mock_attempt_id', None))


def _mock_section_quiz_queryset(spec, program_filters: dict):
    if spec.quiz_flags:
        return Quiz.objects.filter(**spec.quiz_flags, **program_filters)
    return Quiz.objects.filter(
        **program_filters,
        is_listening=False,
        is_reading=False,
        is_essay=False,
        is_speaking=False,
        is_math=False,
    )


def _eligible_quizzes_for_section(
    student_id: int,
    section_key: str,
    exam_program: str,
):
    spec = get_section_spec(exam_program, section_key)
    program_filters = _program_quiz_filters(exam_program)
    if not spec or not program_filters or not student_has_course_access(student_id, exam_program):
        return []

    qs = _mock_section_quiz_queryset(spec, program_filters)
    if spec.sat_sections:
        qs = qs.filter(sat_section__in=spec.sat_sections)
    elif spec.category_names:
        qs = qs.filter(category__name__in=spec.category_names)
    qs = (
        qs.annotate(has_content=_content_filter_for_section(section_key, exam_program))
        .filter(has_content=True)
        .select_related('category')
    )
    return list(qs)


def _eligible_quizzes_for_customer_section(section_key: str, exam_program: str):
    spec = get_section_spec(exam_program, section_key)
    program_filters = _program_quiz_filters(exam_program)
    if not spec or not program_filters:
        return []

    qs = _mock_section_quiz_queryset(spec, program_filters)
    if spec.sat_sections:
        qs = qs.filter(sat_section__in=spec.sat_sections)
    elif spec.category_names:
        qs = qs.filter(category__name__in=spec.category_names)
    qs = (
        qs.annotate(has_content=_content_filter_for_section(section_key, exam_program))
        .filter(has_content=True)
        .select_related('category')
    )
    return list(qs)


def pick_random_section_quizzes(
    student_id: int,
    exam_program: str,
) -> dict[str, Quiz | None]:
    picked: dict[str, Quiz | None] = {}
    for spec in get_program_sections(exam_program):
        candidates = _eligible_quizzes_for_section(student_id, spec.key, exam_program)
        picked[spec.key] = random.choice(candidates) if candidates else None
    return picked


def pick_random_customer_section_quizzes(
    *,
    exam_program: str = IELTS_SERVICE,
) -> dict[str, Quiz | None]:
    picked: dict[str, Quiz | None] = {}
    for spec in get_program_sections(exam_program):
        candidates = _eligible_quizzes_for_customer_section(spec.key, exam_program)
        picked[spec.key] = random.choice(candidates) if candidates else None
    return picked


def pick_random_ielts_section_quizzes(student_id: int) -> dict[str, Quiz | None]:
    exam_program = resolve_student_mock_exam_program(student_id)
    if not exam_program:
        return {spec.key: None for spec in get_program_sections(IELTS_SERVICE)}
    return pick_random_section_quizzes(student_id, exam_program)


def get_missing_mock_sections(student_id: int, exam_program: str) -> list[str]:
    picked = pick_random_section_quizzes(student_id, exam_program)
    return [section for section, quiz in picked.items() if quiz is None]


def get_missing_customer_mock_sections(*, exam_program: str = IELTS_SERVICE) -> list[str]:
    picked = pick_random_customer_section_quizzes(exam_program=exam_program)
    return [section for section, quiz in picked.items() if quiz is None]


def _attempt_create_kwargs(exam_program: str, picked: dict[str, Quiz | None]) -> dict:
    first_section = get_program_first_section(exam_program)
    kwargs = {
        'exam_program': exam_program,
        'status': IeltsMockTestAttempt.Status.IN_PROGRESS,
        'current_section': first_section,
        'listening_quiz': None,
        'reading_quiz': None,
        'writing_quiz': None,
        'speaking_quiz': None,
        'math_quiz': None,
    }
    for spec in get_program_sections(exam_program):
        kwargs[spec.quiz_field] = picked[spec.key]
    if not kwargs.get('reading_quiz'):
        raise ValueError('reading_quiz is required for mock attempts')
    return kwargs


def abandon_in_progress_mock_attempts(student_id: int, *, exam_program: str | None = None) -> None:
    qs = IeltsMockTestAttempt.objects.filter(
        student_id=student_id,
        status=IeltsMockTestAttempt.Status.IN_PROGRESS,
    )
    if exam_program:
        qs = qs.filter(exam_program=exam_program)
    qs.update(status=IeltsMockTestAttempt.Status.ABANDONED)


@transaction.atomic
def start_mock_test_attempt(
    student_id: int,
    exam_program: str,
) -> tuple[IeltsMockTestAttempt | None, str | None]:
    if not is_valid_mock_program(exam_program):
        return None, str(_('Unknown mock test program.'))
    if not student_has_course_access(student_id, exam_program):
        return None, str(_('You are not enrolled in this mock test program.'))
    if not student_can_access_mock_program(student_id, exam_program):
        return None, str(_('Mock test is locked. Ask your teacher to enable it.'))

    picked = pick_random_section_quizzes(student_id, exam_program)
    missing = [section for section, quiz in picked.items() if quiz is None]
    if missing:
        labels = ', '.join(
            get_section_label(exam_program, section)
            for section in missing
        )
        return None, str(_('Not enough quizzes are available for: %(sections)s.') % {'sections': labels})

    abandon_in_progress_mock_attempts(student_id, exam_program=exam_program)

    attempt = IeltsMockTestAttempt.objects.create(
        student_id=student_id,
        **_attempt_create_kwargs(exam_program, picked),
    )
    logger.info(
        'Mock test started attempt_id=%s student_id=%s exam_program=%s',
        attempt.pk,
        student_id,
        exam_program,
    )
    return attempt, None


def get_mock_attempt_for_student(student_id: int, attempt_id: int) -> IeltsMockTestAttempt | None:
    return (
        IeltsMockTestAttempt.objects.filter(
            pk=attempt_id,
            student_id=student_id,
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
            'student__user',
        )
        .first()
    )


def get_active_mock_attempt(student_id: int, attempt_id: int) -> IeltsMockTestAttempt | None:
    attempt = get_mock_attempt_for_student(student_id, attempt_id)
    if not attempt or attempt.status != IeltsMockTestAttempt.Status.IN_PROGRESS:
        return None
    return attempt


def abandon_mock_test_attempt(student_id: int, attempt_id: int) -> None:
    IeltsMockTestAttempt.objects.filter(
        pk=attempt_id,
        student_id=student_id,
        status=IeltsMockTestAttempt.Status.IN_PROGRESS,
    ).update(status=IeltsMockTestAttempt.Status.ABANDONED)


def section_for_quiz_in_attempt(attempt: IeltsMockTestAttempt, quiz_id: int) -> str | None:
    for section_key in attempt.program_section_order():
        quiz = attempt.quiz_for_section(section_key)
        if quiz and quiz.pk == quiz_id:
            return section_key
    return None


def find_in_progress_mock_attempt_for_quiz(
    student_id: int,
    quiz_id: int,
) -> IeltsMockTestAttempt | None:
    return (
        IeltsMockTestAttempt.objects.filter(
            student_id=student_id,
            status=IeltsMockTestAttempt.Status.IN_PROGRESS,
        )
        .filter(
            Q(listening_quiz_id=quiz_id)
            | Q(reading_quiz_id=quiz_id)
            | Q(writing_quiz_id=quiz_id)
            | Q(speaking_quiz_id=quiz_id)
            | Q(math_quiz_id=quiz_id)
        )
        .first()
    )


def validate_mock_section_submit(attempt: IeltsMockTestAttempt, quiz_id: int) -> str | None:
    section = section_for_quiz_in_attempt(attempt, quiz_id)
    if not section:
        return str(_('This quiz is not part of your mock test.'))
    if section != attempt.current_section:
        return str(_('Complete the current mock test section first.'))
    return None


def mock_allows_active_section_take(
    student_id: int,
    mock_attempt_id: int | None,
    quiz_id: int,
) -> bool:
    if not mock_attempt_id:
        return False
    attempt = get_active_mock_attempt(student_id, mock_attempt_id)
    if not attempt:
        return False
    section = section_for_quiz_in_attempt(attempt, quiz_id)
    if not section or section != attempt.current_section:
        return False
    return attempt.result_for_section(section) is None


def get_mock_landing_url(exam_program: str, *, role: str = 'student') -> str:
    if role == 'customer':
        return reverse('portals:customer-mock-landing', kwargs={'program': exam_program})
    return reverse(get_mock_landing_url_name(role), kwargs={'program': exam_program})


def get_mock_complete_url(attempt: IeltsMockTestAttempt, *, role: str = 'student') -> str:
    if role == 'customer':
        return reverse(
            'portals:customer-mock-complete',
            kwargs={'program': attempt.exam_program, 'pk': attempt.pk},
        )
    return reverse(
        get_mock_complete_url_name(role),
        kwargs={'program': attempt.exam_program, 'pk': attempt.pk},
    )


def get_mock_landing_url_name(role: str) -> str:
    from portals.utils.mock_programs import get_mock_landing_url_name as _name

    return _name(role)


def get_mock_complete_url_name(role: str) -> str:
    from portals.utils.mock_programs import get_mock_complete_url_name as _name

    return _name(role)


def get_mock_take_url(
    attempt: IeltsMockTestAttempt,
    section: str,
    *,
    role: str = 'student',
) -> str:
    quiz = attempt.quiz_for_section(section)
    if not quiz:
        return get_mock_landing_url(attempt.exam_program, role=role)

    spec = get_section_spec(attempt.exam_program, section)
    if not spec:
        return get_mock_landing_url(attempt.exam_program, role=role)

    take_kind = resolve_take_url_kind(attempt.exam_program, section, quiz)
    base = reverse(get_take_url_name(role, take_kind), kwargs={'pk': quiz.pk})
    return f'{base}?mock={attempt.pk}'


def get_mock_current_take_url(attempt: IeltsMockTestAttempt, *, role: str = 'student') -> str:
    return get_mock_take_url(attempt, attempt.current_section, role=role)


def resolve_mock_take_request(
    student_id: int,
    mock_id: int | None,
    quiz_id: int,
) -> dict:
    if not mock_id:
        return {}

    attempt = get_mock_attempt_for_student(student_id, mock_id)
    if not attempt:
        logger.warning(
            'Mock take unknown attempt student_id=%s mock_id=%s quiz_id=%s',
            student_id,
            mock_id,
            quiz_id,
        )
        return {'mock_redirect': get_mock_landing_url(IELTS_SERVICE)}

    if attempt.status == IeltsMockTestAttempt.Status.COMPLETED:
        return {'mock_redirect': get_mock_complete_url(attempt)}

    if attempt.status != IeltsMockTestAttempt.Status.IN_PROGRESS:
        return {'mock_redirect': get_mock_landing_url(attempt.exam_program)}

    section = section_for_quiz_in_attempt(attempt, quiz_id)
    if not section or section != attempt.current_section:
        redirect_url = get_mock_current_take_url(attempt)
        logger.info(
            'Mock take redirect stale page attempt_id=%s quiz_id=%s quiz_section=%s current_section=%s redirect=%s',
            attempt.pk,
            quiz_id,
            section,
            attempt.current_section,
            redirect_url,
        )
        return {'mock_redirect': redirect_url}

    return {
        'mock_attempt': serialize_mock_progress(attempt),
        'mock_id': attempt.pk,
        'back_url': get_mock_landing_url(attempt.exam_program),
    }


def resolve_mock_start_request(
    student_id: int,
    mock_id: int | None,
    quiz_id: int,
) -> dict | None:
    if not mock_id:
        return None

    attempt = get_active_mock_attempt(student_id, mock_id)
    if not attempt:
        return {
            'success': False,
            'error': str(_('Mock test session is no longer active.')),
        }

    validation_error = validate_mock_section_submit(attempt, quiz_id)
    if validation_error:
        redirect_url = get_mock_current_take_url(attempt)
        logger.info(
            'Mock start redirect stale page attempt_id=%s quiz_id=%s current_section=%s redirect=%s',
            attempt.pk,
            quiz_id,
            attempt.current_section,
            redirect_url,
        )
        return {
            'success': True,
            'redirect_url': redirect_url,
        }

    return None


def get_mock_next_url(attempt: IeltsMockTestAttempt, completed_section: str, *, role: str = 'student') -> str:
    next_section = get_next_section(attempt.exam_program, completed_section)
    if next_section:
        return get_mock_take_url(attempt, next_section, role=role)
    return get_mock_complete_url(attempt, role=role)


@transaction.atomic
def advance_mock_after_section_submit(
    attempt: IeltsMockTestAttempt,
    *,
    section: str,
    result: QuizResult,
) -> IeltsMockTestAttempt:
    spec = get_section_spec(attempt.exam_program, section)
    if not spec:
        raise ValueError(f'Unknown section {section} for program {attempt.exam_program}')
    setattr(attempt, spec.result_field, result)

    next_section = get_next_section(attempt.exam_program, section)
    if next_section:
        attempt.current_section = next_section
        update_fields = [spec.result_field, 'current_section']
    else:
        attempt.status = IeltsMockTestAttempt.Status.COMPLETED
        attempt.completed_at = timezone.now()
        attempt.current_section = section
        update_fields = [spec.result_field, 'status', 'completed_at', 'current_section']

    attempt.save(update_fields=update_fields)
    return attempt


def apply_mock_submit_result(
    *,
    student_id: int,
    mock_attempt_id: int | None,
    quiz_id: int,
    result: QuizResult,
    response: dict,
    defer_notifications: bool,
) -> dict:
    if not mock_attempt_id:
        return response

    attempt = get_active_mock_attempt(student_id, mock_attempt_id)
    if not attempt:
        logger.warning(
            'Mock test submit rejected: inactive attempt student_id=%s mock_attempt_id=%s quiz_id=%s',
            student_id,
            mock_attempt_id,
            quiz_id,
        )
        response['mock_error'] = str(_('Mock test session is no longer active.'))
        return response

    validation_error = validate_mock_section_submit(attempt, quiz_id)
    if validation_error:
        logger.warning(
            'Mock test submit validation failed attempt_id=%s quiz_id=%s current_section=%s error=%s',
            attempt.pk,
            quiz_id,
            attempt.current_section,
            validation_error,
        )
        response['success'] = False
        response['error'] = validation_error
        response['redirect_url'] = get_mock_current_take_url(attempt)
        return response

    section = section_for_quiz_in_attempt(attempt, quiz_id)
    if not section:
        response['success'] = False
        response['error'] = str(_('Invalid mock test section.'))
        return response

    attempt = advance_mock_after_section_submit(attempt, section=section, result=result)
    next_section = get_next_section(attempt.exam_program, section)
    completed_label = get_section_label(attempt.exam_program, section)
    response['next_url'] = get_mock_next_url(attempt, section)
    response['mock_attempt_id'] = attempt.pk
    response['mock_continue'] = True
    response['mock_completed'] = attempt.status == IeltsMockTestAttempt.Status.COMPLETED
    response['mock_section_completed'] = section
    response['mock_section_completed_label'] = str(completed_label)
    if next_section:
        next_label = get_section_label(attempt.exam_program, next_section)
        response['mock_next_section'] = next_section
        response['mock_next_section_label'] = str(next_label)
        rest_seconds = get_inter_section_rest_seconds(attempt.exam_program, section)
        if rest_seconds:
            response['mock_rest_seconds'] = rest_seconds
            response['mock_continue_message'] = str(
                _('%(completed)s is done. Take a short break before %(next)s.') % {
                    'completed': completed_label,
                    'next': next_label,
                }
            )
        else:
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

    manual_sections = get_manual_sections(attempt.exam_program)
    if attempt.status == IeltsMockTestAttempt.Status.COMPLETED:
        logger.info(
            'Mock test completed attempt_id=%s student_id=%s completed_section=%s result_id=%s next_url=%s',
            attempt.pk,
            student_id,
            section,
            result.pk,
            response['next_url'],
        )
        from portals.utils.notifications import (
            create_mock_section_review_notifications,
            create_mock_test_completed_notifications,
        )

        if section in manual_sections:
            create_mock_section_review_notifications(attempt, result, section)
        create_mock_test_completed_notifications(attempt)
    else:
        logger.info(
            'Mock test section advanced attempt_id=%s student_id=%s completed_section=%s current_section=%s next_section=%s result_id=%s next_url=%s',
            attempt.pk,
            student_id,
            section,
            attempt.current_section,
            next_section,
            result.pk,
            response['next_url'],
        )
        if section in manual_sections:
            from portals.utils.notifications import create_mock_section_review_notifications

            create_mock_section_review_notifications(attempt, result, section)

    return response


def parse_mock_attempt_id(raw) -> int | None:
    if raw in (None, ''):
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def serialize_mock_progress(attempt: IeltsMockTestAttempt) -> dict:
    section = attempt.current_section
    section_label = get_section_label(attempt.exam_program, section)
    index = section_index_for_program(attempt.exam_program, section)
    section_total = len(attempt.program_section_order())
    is_final = is_final_section(attempt.exam_program, section)
    return {
        'id': attempt.pk,
        'exam_program': attempt.exam_program,
        'current_section': section,
        'section_index': index,
        'section_total': section_total,
        'section_label': section_label,
        'is_final_section': is_final,
        'finish_button_label': str(
            _('Finish test') if is_final else _('Finish the section')
        ),
        'progress_label': _('Section %(index)s of %(total)s — %(section)s') % {
            'index': index,
            'total': section_total,
            'section': section_label,
        },
    }


def ielts_round_band(value: float) -> float:
    return math.floor(value * 2 + 0.5) / 2


def section_score_band(total_score, max_score) -> float | None:
    if total_score is None or max_score is None or max_score <= 0:
        return None
    return ielts_round_band((float(total_score) / float(max_score)) * IELTS_BAND_MAX)


def find_mock_attempt_for_result(
    result: QuizResult,
    *,
    status: str | None = None,
) -> IeltsMockTestAttempt | None:
    if not result or not result.pk:
        return None
    if result.ielts_mock_attempt_id:
        attempt = result.ielts_mock_attempt
        if status and attempt.status != status:
            return None
        return attempt
    qs = (
        IeltsMockTestAttempt.objects.filter(
            Q(student_id=result.student_id) | Q(customer_id=result.customer_id),
        )
        .exclude(status=IeltsMockTestAttempt.Status.ABANDONED)
        .filter(
            Q(listening_result_id=result.pk)
            | Q(reading_result_id=result.pk)
            | Q(writing_result_id=result.pk)
            | Q(speaking_result_id=result.pk)
            | Q(math_result_id=result.pk)
        )
    )
    if status:
        qs = qs.filter(status=status)
    return qs.first()


def find_completed_mock_for_result(result: QuizResult) -> IeltsMockTestAttempt | None:
    return find_mock_attempt_for_result(
        result,
        status=IeltsMockTestAttempt.Status.COMPLETED,
    )


def section_for_result_in_attempt(attempt: IeltsMockTestAttempt, result: QuizResult) -> str | None:
    if not attempt or not result:
        return None
    for section in attempt.program_section_order():
        section_result = attempt.result_for_section(section)
        if section_result and section_result.pk == result.pk:
            return section
    return None


def mock_attempt_is_fully_graded(attempt: IeltsMockTestAttempt) -> bool:
    for section in attempt.program_section_order():
        result = attempt.result_for_section(section)
        if not result or result.is_pending_review or result.total_score is None:
            return False
    return True


def maybe_publish_mock_attempt_results(attempt: IeltsMockTestAttempt) -> bool:
    if not mock_attempt_is_fully_graded(attempt):
        return False
    from portals.utils.notifications import create_mock_results_published_notifications

    create_mock_results_published_notifications(attempt)
    return True


def maybe_publish_mock_results_for_result(result: QuizResult) -> None:
    attempt = find_completed_mock_for_result(result)
    if not attempt:
        return
    if attempt.student_id:
        refreshed = get_mock_attempt_for_student(attempt.student_id, attempt.pk)
    else:
        from portals.utils.customer_mock import get_mock_attempt_for_customer

        refreshed = get_mock_attempt_for_customer(attempt.customer_id, attempt.pk)
    if refreshed:
        maybe_publish_mock_attempt_results(refreshed)


def _batch_quiz_max_scores(quizzes) -> dict[int, int]:
    """One typed-count pass + one variant Count for all quizzes on a page."""
    from django.db.models import Count
    from portals.utils.queries import _answerable_question_counts

    unique = []
    seen = set()
    for quiz in quizzes or []:
        if not quiz or quiz.pk in seen:
            continue
        seen.add(quiz.pk)
        unique.append(quiz)
    if not unique:
        return {}

    typed = _answerable_question_counts(unique)
    variant_ids = [
        quiz.pk
        for quiz in unique
        if not quiz.is_manual_grading
        and not quiz.is_reading
        and not quiz.is_math
        and not quiz.is_listening
    ]
    variant_counts = {}
    if variant_ids:
        variant_counts = dict(
            QuizQuestion.objects.filter(quiz_id__in=variant_ids)
            .values('quiz_id')
            .annotate(c=Count('id'))
            .values_list('quiz_id', 'c')
        )

    scores: dict[int, int] = {}
    for quiz in unique:
        if quiz.is_manual_grading:
            scores[quiz.pk] = quiz.MANUAL_REVIEW_MAX_SCORE
        elif quiz.is_reading or quiz.is_math or quiz.is_listening or quiz.is_speaking:
            scores[quiz.pk] = typed.get(quiz.pk, 0)
        else:
            scores[quiz.pk] = int(variant_counts.get(quiz.pk, 0))
    return scores


def serialize_mock_attempt_summary(
    attempt: IeltsMockTestAttempt,
    *,
    max_scores: dict[int, int] | None = None,
) -> dict:
    exam_program = attempt.exam_program
    scoring_mode = get_program_scoring_mode(exam_program)
    auto_sections = get_auto_sections(exam_program)
    manual_sections = get_manual_sections(exam_program)
    section_order = attempt.program_section_order()

    if max_scores is None:
        max_scores = _batch_quiz_max_scores(
            [attempt.quiz_for_section(section) for section in section_order]
        )

    sections = []
    section_scores: list[float] = []
    auto_scores: list[float] = []
    manual_scores: list[float] = []
    auto_score_total = 0.0
    auto_max_total = 0
    manual_score_total = 0.0
    manual_max_total = 0
    pending_review_count = 0

    for section in section_order:
        quiz = attempt.quiz_for_section(section)
        result = attempt.result_for_section(section)
        is_auto_graded = section in auto_sections
        is_manual_graded = section in manual_sections
        is_pending_review = bool(result and result.is_pending_review)
        if is_pending_review:
            pending_review_count += 1

        max_score = max_scores.get(quiz.pk) if quiz else None
        total_score = result.total_score if result else None
        has_final_score = bool(
            result
            and not is_pending_review
            and total_score is not None
            and max_score is not None
        )

        band_score = None
        scaled_score = None
        display_score = None
        display_score_max = None

        if has_final_score:
            if scoring_mode == 'sat_scaled':
                scaled_score = sat_section_scaled_score(total_score, max_score)
                display_score = scaled_score
                display_score_max = SAT_SECTION_SCORE_MAX
                if scaled_score is not None:
                    section_scores.append(float(scaled_score))
                    if is_auto_graded:
                        auto_scores.append(float(scaled_score))
                        auto_score_total += float(total_score)
                        auto_max_total += int(max_score)
            else:
                band_score = section_score_band(total_score, max_score)
                display_score = band_score
                display_score_max = IELTS_BAND_MAX
                if band_score is not None:
                    section_scores.append(band_score)
                    if is_auto_graded:
                        auto_scores.append(band_score)
                        auto_score_total += float(total_score)
                        auto_max_total += int(max_score)
                    elif is_manual_graded:
                        manual_scores.append(band_score)
                        manual_score_total += float(total_score)
                        manual_max_total += int(max_score)

        sections.append({
            'section': section,
            'section_label': get_section_label(exam_program, section, translate=False),
            'quiz_id': quiz.pk if quiz else None,
            'quiz_topic': quiz.topic if quiz else '',
            'result_id': result.pk if result else None,
            'total_score': total_score,
            'max_score': max_score,
            'band_score': band_score,
            'scaled_score': scaled_score,
            'display_score': display_score,
            'display_score_max': display_score_max,
            'is_auto_graded': is_auto_graded,
            'is_manual_graded': is_manual_graded,
            'is_pending_review': is_pending_review,
            'is_reviewed': bool(result and result.reviewed_at),
            'grading_mode_label': quiz.get_grading_mode_label() if quiz else '',
        })

    is_fully_graded = len(section_scores) == len(section_order)
    overall_score = None
    overall_score_max = None
    overall_band = None
    auto_band_average = None
    manual_band_average = None

    if is_fully_graded and scoring_mode == 'sat_scaled':
        overall_score = int(round(sum(section_scores)))
        overall_score_max = SAT_TOTAL_SCORE_MAX
    elif is_fully_graded:
        overall_band = ielts_round_band(sum(section_scores) / len(section_scores))
        overall_score = overall_band
        overall_score_max = IELTS_BAND_MAX
        auto_band_average = (
            ielts_round_band(sum(auto_scores) / len(auto_scores)) if len(auto_scores) == 2 else None
        )
        manual_band_average = (
            ielts_round_band(sum(manual_scores) / len(manual_scores)) if len(manual_scores) == 2 else None
        )

    return {
        'id': attempt.pk,
        'pk': attempt.pk,
        'exam_program': exam_program,
        'exam_program_label': str(PROGRAM_LABELS.get(exam_program, exam_program)),
        'scoring_mode': scoring_mode,
        'status': attempt.status,
        'started_at': attempt.started_at,
        'completed_at': attempt.completed_at,
        'student_name': (
            attempt.student.full_name
            if attempt.student_id
            else (attempt.customer.full_name if attempt.customer_id else '')
        ),
        'contact_phone': (
            (attempt.customer.phone or '').strip()
            if attempt.customer_id and getattr(attempt, 'customer', None) is not None
            else (
                (attempt.student.phone or '').strip()
                if attempt.student_id and getattr(attempt, 'student', None) is not None
                else ''
            )
        ),
        'sections': sections,
        'is_fully_graded': is_fully_graded,
        'pending_review_count': pending_review_count,
        'overall_score': overall_score,
        'overall_score_max': overall_score_max,
        'overall_band': overall_band,
        'overall_band_max': IELTS_BAND_MAX if scoring_mode == 'ielts_band' else None,
        'auto_score_total': auto_score_total if auto_scores else None,
        'auto_max_total': auto_max_total if auto_scores else None,
        'auto_band_average': auto_band_average,
        'manual_score_total': manual_score_total if manual_scores else None,
        'manual_max_total': manual_max_total if manual_scores else None,
        'manual_band_average': manual_band_average,
    }


def serialize_mock_attempt_summaries(attempts) -> list[dict]:
    """Serialize many attempts with one batched max-score lookup."""
    rows = list(attempts or [])
    quizzes = []
    for attempt in rows:
        for section in attempt.program_section_order():
            quiz = attempt.quiz_for_section(section)
            if quiz:
                quizzes.append(quiz)
    max_scores = _batch_quiz_max_scores(quizzes)
    return [
        serialize_mock_attempt_summary(attempt, max_scores=max_scores)
        for attempt in rows
    ]


def get_student_completed_mock_attempts(
    student_id: int,
    *,
    exam_program: str | None = None,
    limit: int = 20,
):
    qs = IeltsMockTestAttempt.objects.filter(
        student_id=student_id,
        status=IeltsMockTestAttempt.Status.COMPLETED,
    )
    if exam_program:
        qs = qs.filter(exam_program=exam_program)
    return (
        qs.select_related(
            'student__user',
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


# Legacy constants kept for tests and gradual migration.
SECTION_SPECS = tuple(
    (spec.key, spec.quiz_flags)
    for spec in get_program_sections(IELTS_SERVICE)
)
RESULT_FIELD_BY_SECTION = {
    spec.key: spec.result_field
    for spec in get_program_sections(IELTS_SERVICE)
}
NEXT_SECTION_BY_SECTION = {
    spec.key: get_next_section(IELTS_SERVICE, spec.key)
    for spec in get_program_sections(IELTS_SERVICE)
}
AUTO_SECTIONS = get_auto_sections(IELTS_SERVICE)
MANUAL_SECTIONS = get_manual_sections(IELTS_SERVICE)

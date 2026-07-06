"""IELTS full mock test session helpers."""

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
from portals.utils.student_courses import quiz_visible_to_student, student_has_course_access


IELTS_SERVICE = 'ielts'

logger = logging.getLogger('portals.ielts_mock')

SECTION_SPECS = (
    (IeltsMockTestAttempt.Section.LISTENING, {'is_listening': True}),
    (IeltsMockTestAttempt.Section.READING, {'is_reading': True}),
    (IeltsMockTestAttempt.Section.WRITING, {'is_essay': True}),
    (IeltsMockTestAttempt.Section.SPEAKING, {'is_speaking': True}),
)

RESULT_FIELD_BY_SECTION = {
    IeltsMockTestAttempt.Section.LISTENING: 'listening_result',
    IeltsMockTestAttempt.Section.READING: 'reading_result',
    IeltsMockTestAttempt.Section.WRITING: 'writing_result',
    IeltsMockTestAttempt.Section.SPEAKING: 'speaking_result',
}

NEXT_SECTION_BY_SECTION = {
    IeltsMockTestAttempt.Section.LISTENING: IeltsMockTestAttempt.Section.READING,
    IeltsMockTestAttempt.Section.READING: IeltsMockTestAttempt.Section.WRITING,
    IeltsMockTestAttempt.Section.WRITING: IeltsMockTestAttempt.Section.SPEAKING,
    IeltsMockTestAttempt.Section.SPEAKING: None,
}

AUTO_SECTIONS = frozenset({
    IeltsMockTestAttempt.Section.LISTENING,
    IeltsMockTestAttempt.Section.READING,
})
MANUAL_SECTIONS = frozenset({
    IeltsMockTestAttempt.Section.WRITING,
    IeltsMockTestAttempt.Section.SPEAKING,
})
IELTS_BAND_MAX = 9.0


def student_can_access_ielts_mock(student_id: int) -> bool:
    return student_has_course_access(student_id, IELTS_SERVICE)


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


def _content_filter_for_section(section: str):
    if section == IeltsMockTestAttempt.Section.LISTENING:
        return _listening_quiz_has_content()
    if section == IeltsMockTestAttempt.Section.READING:
        return _reading_quiz_has_content()
    if section == IeltsMockTestAttempt.Section.WRITING:
        return _essay_quiz_has_content()
    if section == IeltsMockTestAttempt.Section.SPEAKING:
        return _speaking_quiz_has_content()
    return Q(pk__in=[])


def standalone_quiz_results(**filters):
    """Quiz results from normal (non-mock) attempts only."""
    return QuizResult.objects.filter(ielts_mock_attempt__isnull=True, **filters)


def is_mock_quiz_result(result: QuizResult | None) -> bool:
    return bool(result and getattr(result, 'ielts_mock_attempt_id', None))


def _eligible_quizzes_for_section(student_id: int, section: str, flag_kwargs: dict):
    qs = (
        Quiz.objects.filter(
            category__service=IELTS_SERVICE,
            **flag_kwargs,
        )
        .annotate(has_content=_content_filter_for_section(section))
        .filter(has_content=True)
    )
    candidates = [quiz for quiz in qs if quiz_visible_to_student(quiz, student_id)]
    return candidates


def pick_random_ielts_section_quizzes(student_id: int) -> dict[str, Quiz | None]:
    picked: dict[str, Quiz | None] = {}
    for section, flag_kwargs in SECTION_SPECS:
        candidates = _eligible_quizzes_for_section(student_id, section, flag_kwargs)
        picked[section] = random.choice(candidates) if candidates else None
    return picked


def get_missing_mock_sections(student_id: int) -> list[str]:
    picked = pick_random_ielts_section_quizzes(student_id)
    return [section for section, quiz in picked.items() if quiz is None]


def abandon_in_progress_mock_attempts(student_id: int) -> None:
    IeltsMockTestAttempt.objects.filter(
        student_id=student_id,
        status=IeltsMockTestAttempt.Status.IN_PROGRESS,
    ).update(status=IeltsMockTestAttempt.Status.ABANDONED)


@transaction.atomic
def start_mock_test_attempt(student_id: int) -> tuple[IeltsMockTestAttempt | None, str | None]:
    # Pick once and reuse: validating with one random draw and creating with
    # a second draw could select different quizzes (or fail the second time).
    picked = pick_random_ielts_section_quizzes(student_id)
    missing = [section for section, quiz in picked.items() if quiz is None]
    if missing:
        labels = ', '.join(
            str(dict(IeltsMockTestAttempt.Section.choices).get(section, section))
            for section in missing
        )
        return None, str(_('Not enough quizzes are available for: %(sections)s.') % {'sections': labels})

    abandon_in_progress_mock_attempts(student_id)

    attempt = IeltsMockTestAttempt.objects.create(
        student_id=student_id,
        status=IeltsMockTestAttempt.Status.IN_PROGRESS,
        current_section=IeltsMockTestAttempt.Section.LISTENING,
        listening_quiz=picked[IeltsMockTestAttempt.Section.LISTENING],
        reading_quiz=picked[IeltsMockTestAttempt.Section.READING],
        writing_quiz=picked[IeltsMockTestAttempt.Section.WRITING],
        speaking_quiz=picked[IeltsMockTestAttempt.Section.SPEAKING],
    )
    logger.info(
        'Mock test started attempt_id=%s student_id=%s listening_quiz=%s reading_quiz=%s writing_quiz=%s speaking_quiz=%s',
        attempt.pk,
        student_id,
        attempt.listening_quiz_id,
        attempt.reading_quiz_id,
        attempt.writing_quiz_id,
        attempt.speaking_quiz_id,
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
            'listening_result',
            'reading_result',
            'writing_result',
            'speaking_result',
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
    if attempt.listening_quiz_id == quiz_id:
        return IeltsMockTestAttempt.Section.LISTENING
    if attempt.reading_quiz_id == quiz_id:
        return IeltsMockTestAttempt.Section.READING
    if attempt.writing_quiz_id == quiz_id:
        return IeltsMockTestAttempt.Section.WRITING
    if attempt.speaking_quiz_id == quiz_id:
        return IeltsMockTestAttempt.Section.SPEAKING
    return None


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
    """Allow taking the quiz when it is the student's current mock section without a saved result."""
    if not mock_attempt_id:
        return False
    attempt = get_active_mock_attempt(student_id, mock_attempt_id)
    if not attempt:
        return False
    section = section_for_quiz_in_attempt(attempt, quiz_id)
    if not section or section != attempt.current_section:
        return False
    return attempt.result_for_section(section) is None


def get_mock_current_take_url(attempt: IeltsMockTestAttempt) -> str:
    return get_mock_take_url(attempt, attempt.current_section)


def resolve_mock_take_request(
    student_id: int,
    mock_id: int | None,
    quiz_id: int,
) -> dict:
    """Return mock take template context or a redirect URL for stale mock pages."""
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
        return {'mock_redirect': reverse('portals:student-ielts-mock')}

    if attempt.status == IeltsMockTestAttempt.Status.COMPLETED:
        return {
            'mock_redirect': reverse(
                'portals:student-ielts-mock-complete',
                kwargs={'pk': attempt.pk},
            ),
        }

    if attempt.status != IeltsMockTestAttempt.Status.IN_PROGRESS:
        return {'mock_redirect': reverse('portals:student-ielts-mock')}

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
        'back_url': reverse('portals:student-ielts-mock'),
    }


def resolve_mock_start_request(
    student_id: int,
    mock_id: int | None,
    quiz_id: int,
) -> dict | None:
    """Validate mock quiz start; return redirect payload when the client is on a stale page."""
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


def get_mock_take_url(attempt: IeltsMockTestAttempt, section: str) -> str:
    quiz = attempt.quiz_for_section(section)
    if not quiz:
        return reverse('portals:student-ielts-mock')

    if section == IeltsMockTestAttempt.Section.LISTENING:
        url_name = 'portals:student-manual-quiz-take'
    elif section == IeltsMockTestAttempt.Section.READING:
        url_name = 'portals:student-reading-quiz-take'
    elif section == IeltsMockTestAttempt.Section.WRITING:
        url_name = 'portals:student-manual-quiz-take'
    elif section == IeltsMockTestAttempt.Section.SPEAKING:
        url_name = 'portals:student-speaking-quiz-take'
    else:
        return reverse('portals:student-ielts-mock')

    base = reverse(url_name, kwargs={'pk': quiz.pk})
    return f'{base}?mock={attempt.pk}'


def get_mock_next_url(attempt: IeltsMockTestAttempt, completed_section: str) -> str:
    next_section = NEXT_SECTION_BY_SECTION.get(completed_section)
    if next_section:
        return get_mock_take_url(attempt, next_section)
    return reverse('portals:student-ielts-mock-complete', kwargs={'pk': attempt.pk})


@transaction.atomic
def advance_mock_after_section_submit(
    attempt: IeltsMockTestAttempt,
    *,
    section: str,
    result: QuizResult,
) -> IeltsMockTestAttempt:
    result_field = RESULT_FIELD_BY_SECTION[section]
    setattr(attempt, result_field, result)

    next_section = NEXT_SECTION_BY_SECTION.get(section)
    if next_section:
        attempt.current_section = next_section
        update_fields = [result_field, 'current_section']
    else:
        attempt.status = IeltsMockTestAttempt.Status.COMPLETED
        attempt.completed_at = timezone.now()
        attempt.current_section = section
        update_fields = [result_field, 'status', 'completed_at', 'current_section']

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
    next_section = NEXT_SECTION_BY_SECTION.get(section)
    section_labels = dict(IeltsMockTestAttempt.Section.choices)
    completed_label = section_labels.get(section, section)
    response['next_url'] = get_mock_next_url(attempt, section)
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

        if section in MANUAL_SECTIONS:
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
        if section in MANUAL_SECTIONS:
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
    section_label = dict(IeltsMockTestAttempt.Section.choices).get(section, section)
    index = attempt.section_index(section)
    is_final_section = section == IeltsMockTestAttempt.Section.SPEAKING
    return {
        'id': attempt.pk,
        'current_section': section,
        'section_index': index,
        'section_total': len(IeltsMockTestAttempt.SECTION_ORDER),
        'section_label': section_label,
        'is_final_section': is_final_section,
        'finish_button_label': str(
            _('Finish test') if is_final_section else _('Finish the section')
        ),
        'progress_label': _('Section %(index)s of %(total)s — %(section)s') % {
            'index': index,
            'total': len(IeltsMockTestAttempt.SECTION_ORDER),
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
            student_id=result.student_id,
        )
        .exclude(status=IeltsMockTestAttempt.Status.ABANDONED)
        .filter(
            Q(listening_result_id=result.pk)
            | Q(reading_result_id=result.pk)
            | Q(writing_result_id=result.pk)
            | Q(speaking_result_id=result.pk)
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
    for section in IeltsMockTestAttempt.SECTION_ORDER:
        section_result = attempt.result_for_section(section)
        if section_result and section_result.pk == result.pk:
            return section
    return None


def mock_attempt_is_fully_graded(attempt: IeltsMockTestAttempt) -> bool:
    for section in IeltsMockTestAttempt.SECTION_ORDER:
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
    refreshed = get_mock_attempt_for_student(attempt.student_id, attempt.pk)
    if refreshed:
        maybe_publish_mock_attempt_results(refreshed)


def serialize_mock_attempt_summary(attempt: IeltsMockTestAttempt) -> dict:
    sections = []
    section_bands: list[float] = []
    auto_bands: list[float] = []
    manual_bands: list[float] = []
    auto_score_total = 0.0
    auto_max_total = 0
    manual_score_total = 0.0
    manual_max_total = 0
    pending_review_count = 0

    for section in IeltsMockTestAttempt.SECTION_ORDER:
        quiz = attempt.quiz_for_section(section)
        result = attempt.result_for_section(section)
        is_auto_graded = section in AUTO_SECTIONS
        is_manual_graded = section in MANUAL_SECTIONS
        is_pending_review = bool(result and result.is_pending_review)
        if is_pending_review:
            pending_review_count += 1

        max_score = quiz.score_max_value() if quiz else None
        total_score = result.total_score if result else None
        has_final_score = bool(
            result
            and not is_pending_review
            and total_score is not None
            and max_score is not None
        )
        band_score = section_score_band(total_score, max_score) if has_final_score else None
        if band_score is not None:
            section_bands.append(band_score)
            if is_auto_graded:
                auto_bands.append(band_score)
                auto_score_total += float(total_score)
                auto_max_total += int(max_score)
            elif is_manual_graded:
                manual_bands.append(band_score)
                manual_score_total += float(total_score)
                manual_max_total += int(max_score)

        sections.append({
            'section': section,
            'section_label': dict(IeltsMockTestAttempt.Section.choices).get(section, section),
            'quiz_id': quiz.pk if quiz else None,
            'quiz_topic': quiz.topic if quiz else '',
            'result_id': result.pk if result else None,
            'total_score': total_score,
            'max_score': max_score,
            'band_score': band_score,
            'is_auto_graded': is_auto_graded,
            'is_manual_graded': is_manual_graded,
            'is_pending_review': is_pending_review,
            'is_reviewed': bool(result and result.reviewed_at),
            'grading_mode_label': quiz.get_grading_mode_label() if quiz else '',
        })

    is_fully_graded = len(section_bands) == len(IeltsMockTestAttempt.SECTION_ORDER)
    overall_band = ielts_round_band(sum(section_bands) / len(section_bands)) if is_fully_graded else None
    auto_band_average = (
        ielts_round_band(sum(auto_bands) / len(auto_bands)) if len(auto_bands) == 2 else None
    )
    manual_band_average = (
        ielts_round_band(sum(manual_bands) / len(manual_bands)) if len(manual_bands) == 2 else None
    )

    return {
        'id': attempt.pk,
        'pk': attempt.pk,
        'status': attempt.status,
        'started_at': attempt.started_at,
        'completed_at': attempt.completed_at,
        'student_name': attempt.student.full_name,
        'sections': sections,
        'is_fully_graded': is_fully_graded,
        'pending_review_count': pending_review_count,
        'overall_band': overall_band,
        'overall_band_max': IELTS_BAND_MAX,
        'auto_score_total': auto_score_total if len(auto_bands) == 2 else None,
        'auto_max_total': auto_max_total if len(auto_bands) == 2 else None,
        'auto_band_average': auto_band_average,
        'manual_score_total': manual_score_total if len(manual_bands) == 2 else None,
        'manual_max_total': manual_max_total if len(manual_bands) == 2 else None,
        'manual_band_average': manual_band_average,
    }


def get_student_completed_mock_attempts(student_id: int, *, limit: int = 20):
    return (
        IeltsMockTestAttempt.objects.filter(
            student_id=student_id,
            status=IeltsMockTestAttempt.Status.COMPLETED,
        )
        .select_related(
            'student__user',
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

"""Portal quiz score notifications for teachers, parents, and students."""

from __future__ import annotations

from datetime import timedelta

from django.db.models import Prefetch
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from portals.models import (
    ParentProfile,
    PortalNotification,
    QuizQuestion,
    QuizResult,
    QuizResultReview,
    StudyGroup,
)
from portals.utils.cache_utils import cached_query
from portals.utils.portal_services import expand_course_types_to_service_slugs
from portals.utils.queries import serialize_quiz_question
from portals.utils.student_courses import get_quiz_service_code, teacher_can_see_quiz_result


def is_quiz_result_published(result: QuizResult) -> bool:
    """Score is visible to student/parent only after auto-grade or teacher review."""
    quiz = result.quiz
    if quiz.is_manual_grading:
        return bool(result.reviewed_at) and result.total_score is not None
    return result.total_score is not None


def _teacher_ids_for_quiz_result(result: QuizResult) -> set[int]:
    service = get_quiz_service_code(result.quiz)
    if not service:
        return set()
    slugs = expand_course_types_to_service_slugs([service])
    if not slugs:
        return set()
    teacher_ids = set(
        StudyGroup.objects.filter(
            students__pk=result.student_id,
            is_active=True,
            courses__slug__in=slugs,
        )
        .values_list('teacher_id', flat=True)
        .distinct()
    )
    return teacher_ids


def _teacher_ids_for_mock_attempt(attempt) -> set[int]:
    slugs = expand_course_types_to_service_slugs(['ielts'])
    if not slugs:
        return set()
    return set(
        StudyGroup.objects.filter(
            students__pk=attempt.student_id,
            is_active=True,
            courses__slug__in=slugs,
        )
        .values_list('teacher_id', flat=True)
        .distinct()
    )


def create_mock_test_completed_notifications(attempt) -> None:
    """Mock manual sections use the standard teacher review queue, not the bell."""
    return


def create_mock_section_review_notifications(attempt, result: QuizResult, section: str) -> None:
    """Mock writing/speaking appear in Quizzes to review like standalone manual quizzes."""
    return


def create_mock_results_published_notifications(attempt) -> None:
    from portals.models import IeltsMockTestAttempt
    from portals.utils.ielts_mock_test import mock_attempt_is_fully_graded, serialize_mock_attempt_summary

    if attempt.status != IeltsMockTestAttempt.Status.COMPLETED:
        return
    if not mock_attempt_is_fully_graded(attempt):
        return

    summary = serialize_mock_attempt_summary(attempt)
    if summary['overall_band'] is None:
        return

    defaults = {
        'is_read': False,
        'quiz_result': None,
    }
    PortalNotification.objects.update_or_create(
        student_id=attempt.student_id,
        ielts_mock_test=attempt,
        kind=PortalNotification.Kind.MOCK_TEST_RESULTS_PUBLISHED,
        defaults=defaults,
    )
    for parent_id in (
        ParentProfile.objects.filter(students__pk=attempt.student_id)
        .values_list('pk', flat=True)
        .distinct()
    ):
        PortalNotification.objects.update_or_create(
            parent_id=parent_id,
            ielts_mock_test=attempt,
            kind=PortalNotification.Kind.MOCK_TEST_RESULTS_PUBLISHED,
            defaults=defaults,
        )


def create_teacher_submission_notifications(result: QuizResult) -> None:
    """Manual quiz submitted — teachers use the review queue, not the bell list."""
    PortalNotification.objects.filter(
        quiz_result=result,
        kind=PortalNotification.Kind.SUBMISSION_PENDING,
        teacher__isnull=False,
    ).delete()


def create_student_submission_notification(result: QuizResult) -> None:
    """Tell the student their manual quiz was sent for review."""
    if not result.quiz.is_manual_grading:
        return
    PortalNotification.objects.update_or_create(
        student_id=result.student_id,
        quiz_result=result,
        defaults={
            'kind': PortalNotification.Kind.SUBMISSION_PENDING,
            'is_read': False,
        },
    )


def clear_published_result_notifications(result: QuizResult) -> None:
    """Remove stale score alerts when a manual quiz goes back to pending review."""
    PortalNotification.objects.filter(
        quiz_result=result,
        kind=PortalNotification.Kind.RESULT_PUBLISHED,
    ).delete()


def dismiss_student_submission_notification(result: QuizResult) -> None:
    """Remove the student's pending-review alert once the score is published."""
    PortalNotification.objects.filter(
        student_id=result.student_id,
        quiz_result=result,
        kind=PortalNotification.Kind.SUBMISSION_PENDING,
    ).delete()


def _upsert_published_notification(**lookup) -> None:
    PortalNotification.objects.update_or_create(
        **lookup,
        defaults={
            'is_read': False,
            'kind': PortalNotification.Kind.RESULT_PUBLISHED,
        },
    )


def create_published_result_notifications(
    result: QuizResult,
    *,
    exclude_teacher_id: int | None = None,
    notify_teachers: bool = True,
) -> None:
    if not is_quiz_result_published(result):
        return

    if notify_teachers:
        for teacher_id in _teacher_ids_for_quiz_result(result):
            if exclude_teacher_id and teacher_id == exclude_teacher_id:
                continue
            _upsert_published_notification(
                teacher_id=teacher_id,
                quiz_result=result,
                kind=PortalNotification.Kind.RESULT_PUBLISHED,
            )

    if result.quiz.is_manual_grading:
        dismiss_student_submission_notification(result)
        _upsert_published_notification(
            student_id=result.student_id,
            quiz_result=result,
        )

    for parent_id in (
        ParentProfile.objects.filter(students__pk=result.student_id)
        .values_list('pk', flat=True)
        .distinct()
    ):
        _upsert_published_notification(
            parent_id=parent_id,
            quiz_result=result,
        )


def create_weekly_score_published_notifications(record) -> None:
    """Notify student and linked parents when a weekly score is saved."""
    from portals.models import ParentProfile, WeeklyStudentScore

    if not isinstance(record, WeeklyStudentScore) or not record.pk:
        return

    defaults = {
        'is_read': False,
        'kind': PortalNotification.Kind.WEEKLY_SCORE_PUBLISHED,
        'quiz_result': None,
        'ielts_mock_test': None,
    }
    PortalNotification.objects.update_or_create(
        student_id=record.student_id,
        weekly_student_score_id=record.pk,
        defaults=defaults,
    )
    for parent_id in (
        ParentProfile.objects.filter(students__pk=record.student_id)
        .values_list('pk', flat=True)
        .distinct()
    ):
        PortalNotification.objects.update_or_create(
            parent_id=parent_id,
            weekly_student_score_id=record.pk,
            defaults=defaults,
        )


def _weekly_score_detail_url(*, role: str) -> str:
    routes = {
        'parent': 'portals:parent-scores',
        'student': 'portals:student-scores',
    }
    return reverse(routes[role])


def _serialize_weekly_score_notification(row: PortalNotification, *, role: str) -> dict:
    from portals.models.score_models import WEEKLY_SCORE_MAX

    record = row.weekly_student_score
    if not record:
        return {
            'id': row.pk,
            'kind': row.kind,
            'is_submission_pending': False,
            'is_weekly_score': True,
            'is_read': row.is_read,
            'created_at': row.created_at,
            'student_name': '',
            'quiz_topic': '',
            'grading_mode_label': '',
            'total_score': None,
            'max_value': None,
            'score_detail_url': '',
            'review_url': '',
            'mark_read_url': reverse('portals:notification-mark-read', kwargs={'pk': row.pk}),
            'delete_url': reverse('portals:notification-delete', kwargs={'pk': row.pk}),
        }

    week_end = record.week_start + timedelta(days=6)
    week_label = f'{record.week_start:%d.%m.%Y} – {week_end:%d.%m.%Y}'
    return {
        'id': row.pk,
        'kind': row.kind,
        'is_submission_pending': False,
        'is_weekly_score': True,
        'is_read': row.is_read,
        'created_at': row.created_at,
        'student_name': record.student.full_name,
        'quiz_topic': week_label,
        'week_label': week_label,
        'teacher_name': record.teacher.full_name,
        'grading_mode_label': _('Weekly assessment'),
        'total_score': float(record.score),
        'max_value': WEEKLY_SCORE_MAX,
        'score_detail_url': _weekly_score_detail_url(role=role),
        'review_url': '',
        'mark_read_url': reverse('portals:notification-mark-read', kwargs={'pk': row.pk}),
        'delete_url': reverse('portals:notification-delete', kwargs={'pk': row.pk}),
    }


def dismiss_teacher_submission_notifications(result: QuizResult, *, teacher_id: int | None = None) -> None:
    qs = PortalNotification.objects.filter(
        quiz_result=result,
        kind__in=(
            PortalNotification.Kind.SUBMISSION_PENDING,
            PortalNotification.Kind.MOCK_TEST_SECTION_REVIEW,
        ),
    )
    if teacher_id:
        qs = qs.filter(teacher_id=teacher_id)
    qs.update(is_read=True)


# Backward-compatible alias
create_quiz_result_notifications = create_published_result_notifications


def _notification_queryset(
    *,
    teacher_id: int | None = None,
    parent_id: int | None = None,
    student_id: int | None = None,
    teacher_kind: str | None = PortalNotification.Kind.RESULT_PUBLISHED,
):
    qs = PortalNotification.objects.select_related(
        'quiz_result__student__user',
        'quiz_result__quiz__category',
        'ielts_mock_test__student__user',
        'weekly_student_score__student__user',
        'weekly_student_score__teacher__user',
    ).order_by('-created_at', '-id')
    if teacher_id:
        qs = qs.filter(teacher_id=teacher_id)
        if teacher_kind:
            qs = qs.filter(kind=teacher_kind)
        return qs
    if parent_id:
        return qs.filter(parent_id=parent_id)
    if student_id:
        return qs.filter(student_id=student_id)
    return qs.none()


def _apply_period_filter(qs, period: str | None):
    if not period or period == 'all':
        return qs
    now = timezone.now()
    if period == 'day':
        start = now - timedelta(days=1)
    elif period == 'week':
        start = now - timedelta(days=7)
    elif period == 'month':
        start = now - timedelta(days=30)
    elif period == 'year':
        start = now - timedelta(days=365)
    else:
        return qs
    return qs.filter(created_at__gte=start)


@cached_query(timeout='CACHE_TIMEOUT_SHORT')
def get_teacher_pending_review_count(teacher_id: int) -> int:
    """Cached: runs in the context processor on every teacher portal page."""
    from portals.utils.queries import _teacher_pending_quiz_results_queryset
    from portals.utils.student_courses import filter_quiz_results_for_teacher

    qs = _teacher_pending_quiz_results_queryset(teacher_id)
    if qs is None:
        return 0
    return len(filter_quiz_results_for_teacher(qs[:100], teacher_id))


@cached_query(timeout='CACHE_TIMEOUT_SHORT')
def get_teacher_portal_bell_count(teacher_id: int) -> int:
    """Unread published-result notifications for teachers."""
    return PortalNotification.objects.filter(
        teacher_id=teacher_id,
        is_read=False,
        kind=PortalNotification.Kind.RESULT_PUBLISHED,
    ).count()


def get_unread_notification_count(
    *,
    teacher_id: int | None = None,
    parent_id: int | None = None,
    student_id: int | None = None,
) -> int:
    if teacher_id:
        return get_teacher_portal_bell_count(teacher_id)
    return _notification_queryset(
        teacher_id=teacher_id,
        parent_id=parent_id,
        student_id=student_id,
    ).filter(is_read=False).count()


def _score_detail_url(*, role: str, result_pk: int) -> str:
    routes = {
        'teacher': 'portals:teacher-score-detail',
        'parent': 'portals:parent-score-detail',
        'student': 'portals:student-score-detail',
    }
    return reverse(routes[role], kwargs={'result_pk': result_pk})


def serialize_notification(row: PortalNotification, *, role: str) -> dict:
    if row.kind == PortalNotification.Kind.WEEKLY_SCORE_PUBLISHED and row.weekly_student_score_id:
        return _serialize_weekly_score_notification(row, role=role)

    if row.kind == PortalNotification.Kind.MOCK_TEST_COMPLETED and row.ielts_mock_test_id:
        from portals.utils.ielts_mock_test import serialize_mock_attempt_summary

        attempt = row.ielts_mock_test
        summary = serialize_mock_attempt_summary(attempt)
        detail_url = reverse('portals:teacher-ielts-mock-detail', kwargs={'pk': attempt.pk})
        pending_labels = [
            section['section_label']
            for section in summary['sections']
            if section['is_pending_review']
        ]
        grading_label = _('IELTS mock test — review required')
        if pending_labels:
            grading_label = _('IELTS mock test — review %(sections)s') % {
                'sections': ', '.join(str(label) for label in pending_labels),
            }
        return {
            'id': row.pk,
            'kind': row.kind,
            'is_submission_pending': False,
            'is_mock_test_completed': True,
            'is_mock_notification': True,
            'is_read': row.is_read,
            'created_at': row.created_at,
            'student_name': attempt.student.full_name,
            'quiz_topic': _('IELTS Mock Test'),
            'grading_mode_label': grading_label,
            'total_score': None,
            'max_value': None,
            'score_detail_url': detail_url,
            'review_url': detail_url if role == 'teacher' else '',
            'mark_read_url': reverse('portals:notification-mark-read', kwargs={'pk': row.pk}),
            'delete_url': reverse('portals:notification-delete', kwargs={'pk': row.pk}),
        }

    if row.kind == PortalNotification.Kind.MOCK_TEST_SECTION_REVIEW and row.quiz_result_id:
        from portals.utils.ielts_mock_test import find_mock_attempt_for_result, section_for_result_in_attempt

        result = row.quiz_result
        attempt = row.ielts_mock_test or find_mock_attempt_for_result(result)
        quiz = result.quiz
        section_label = ''
        if attempt:
            section = section_for_result_in_attempt(attempt, result)
            if section:
                from portals.models import IeltsMockTestAttempt

                section_label = dict(IeltsMockTestAttempt.Section.choices).get(section, section)
        mock_detail_url = (
            reverse('portals:teacher-ielts-mock-detail', kwargs={'pk': attempt.pk})
            if attempt
            else ''
        )
        review_url = reverse('portals:teacher-quiz-result-review', kwargs={'result_pk': result.pk})
        topic = _('IELTS Mock Test')
        if section_label:
            topic = _('IELTS Mock Test — %(section)s') % {'section': section_label}
        return {
            'id': row.pk,
            'kind': row.kind,
            'is_submission_pending': True,
            'is_mock_section_review': True,
            'is_mock_notification': True,
            'is_read': row.is_read,
            'created_at': row.created_at,
            'student_name': result.student.full_name,
            'quiz_topic': topic,
            'grading_mode_label': _('Mock test section'),
            'total_score': None,
            'max_value': None,
            'score_detail_url': mock_detail_url or review_url,
            'review_url': review_url if role == 'teacher' else '',
            'mark_read_url': reverse('portals:notification-mark-read', kwargs={'pk': row.pk}),
            'delete_url': reverse('portals:notification-delete', kwargs={'pk': row.pk}),
        }

    if row.kind == PortalNotification.Kind.MOCK_TEST_RESULTS_PUBLISHED and row.ielts_mock_test_id:
        from portals.utils.ielts_mock_test import serialize_mock_attempt_summary

        attempt = row.ielts_mock_test
        summary = serialize_mock_attempt_summary(attempt)
        if role == 'teacher':
            detail_url = reverse('portals:teacher-ielts-mock-detail', kwargs={'pk': attempt.pk})
        else:
            detail_url = reverse('portals:student-ielts-mock-complete', kwargs={'pk': attempt.pk})
        return {
            'id': row.pk,
            'kind': row.kind,
            'is_submission_pending': False,
            'is_mock_test_results': True,
            'is_read': row.is_read,
            'created_at': row.created_at,
            'student_name': attempt.student.full_name,
            'quiz_topic': _('IELTS Mock Test'),
            'grading_mode_label': _('Overall mock test result'),
            'total_score': summary['overall_band'],
            'max_value': summary['overall_band_max'],
            'score_detail_url': detail_url,
            'review_url': '',
            'mark_read_url': reverse('portals:notification-mark-read', kwargs={'pk': row.pk}),
            'delete_url': reverse('portals:notification-delete', kwargs={'pk': row.pk}),
        }

    result = row.quiz_result
    if not result:
        return {
            'id': row.pk,
            'kind': row.kind,
            'is_submission_pending': False,
            'is_read': row.is_read,
            'created_at': row.created_at,
            'student_name': '',
            'quiz_topic': '',
            'grading_mode_label': '',
            'total_score': None,
            'max_value': None,
            'score_detail_url': '',
            'review_url': '',
            'mark_read_url': reverse('portals:notification-mark-read', kwargs={'pk': row.pk}),
            'delete_url': reverse('portals:notification-delete', kwargs={'pk': row.pk}),
        }

    quiz = result.quiz
    max_value = quiz.score_max_value()
    is_pending = row.kind == PortalNotification.Kind.SUBMISSION_PENDING
    if is_pending and role == 'student':
        score_detail_url = reverse('portals:student-scores')
    else:
        score_detail_url = _score_detail_url(role=role, result_pk=result.pk)
    return {
        'id': row.pk,
        'kind': row.kind,
        'is_submission_pending': is_pending,
        'is_read': row.is_read,
        'created_at': row.created_at,
        'student_name': result.student.full_name,
        'quiz_topic': quiz.topic,
        'grading_mode_label': quiz.get_grading_mode_label(),
        'total_score': result.total_score,
        'max_value': max_value,
        'score_detail_url': score_detail_url,
        'review_url': reverse('portals:teacher-quiz-result-review', kwargs={'result_pk': result.pk}) if is_pending and role == 'teacher' else '',
        'mark_read_url': reverse('portals:notification-mark-read', kwargs={'pk': row.pk}),
        'delete_url': reverse('portals:notification-delete', kwargs={'pk': row.pk}),
    }


def get_notifications(
    *,
    teacher_id: int | None = None,
    parent_id: int | None = None,
    student_id: int | None = None,
    period: str | None = None,
):
    if teacher_id:
        role = 'teacher'
        qs = PortalNotification.objects.filter(
            teacher_id=teacher_id,
            kind=PortalNotification.Kind.RESULT_PUBLISHED,
        ).select_related(
            'quiz_result__student__user',
            'quiz_result__quiz__category',
            'ielts_mock_test__student__user',
            'weekly_student_score__student__user',
            'weekly_student_score__teacher__user',
        ).order_by('-created_at', '-id')
    elif parent_id:
        role = 'parent'
        qs = _notification_queryset(parent_id=parent_id)
    else:
        role = 'student'
        qs = _notification_queryset(student_id=student_id)
    qs = _apply_period_filter(qs, period)
    return [serialize_notification(row, role=role) for row in qs[:200]]


def get_notification_for_recipient(
    *,
    notification_id: int,
    teacher_id: int | None = None,
    parent_id: int | None = None,
    student_id: int | None = None,
):
    qs = PortalNotification.objects.filter(pk=notification_id)
    if teacher_id:
        qs = qs.filter(teacher_id=teacher_id)
    elif parent_id:
        qs = qs.filter(parent_id=parent_id)
    elif student_id:
        qs = qs.filter(student_id=student_id)
    else:
        return None
    return qs.first()


def mark_notification_read(
    *,
    notification_id: int,
    teacher_id: int | None = None,
    parent_id: int | None = None,
    student_id: int | None = None,
) -> bool:
    row = get_notification_for_recipient(
        notification_id=notification_id,
        teacher_id=teacher_id,
        parent_id=parent_id,
        student_id=student_id,
    )
    if not row or row.is_read:
        return bool(row)
    row.is_read = True
    row.save(update_fields=['is_read'])
    return True


def delete_notification(
    *,
    notification_id: int,
    teacher_id: int | None = None,
    parent_id: int | None = None,
    student_id: int | None = None,
) -> bool:
    row = get_notification_for_recipient(
        notification_id=notification_id,
        teacher_id=teacher_id,
        parent_id=parent_id,
        student_id=student_id,
    )
    if not row:
        return False
    row.delete()
    return True


def mark_all_notifications_read(
    *,
    teacher_id: int | None = None,
    parent_id: int | None = None,
    student_id: int | None = None,
) -> int:
    qs = _notification_queryset(
        teacher_id=teacher_id,
        parent_id=parent_id,
        student_id=student_id,
    ).filter(is_read=False)
    return qs.update(is_read=True)


def parent_can_view_quiz_result(parent_id: int, result: QuizResult) -> bool:
    if not is_quiz_result_published(result):
        return False
    return ParentProfile.objects.filter(pk=parent_id, students__pk=result.student_id).exists()


def student_can_view_quiz_result(student_id: int, result: QuizResult) -> bool:
    return result.student_id == student_id and is_quiz_result_published(result)


def _build_variant_breakdown(result: QuizResult) -> list[dict]:
    given = result.given_answers or {}
    quiz = result.quiz
    questions = list(quiz.questions.order_by('order', 'id'))

    breakdown = []
    for question in questions:
        selected_raw = given.get(str(question.pk), given.get(question.pk))
        selected_index = None
        if selected_raw is not None and selected_raw != '':
            try:
                selected_index = int(selected_raw)
            except (TypeError, ValueError):
                selected_index = None
        options = question.answer_options or []
        correct_index = question.correct_option_index
        correct = (question.correct_answer or '').strip()
        if correct and correct in options:
            correct_index = options.index(correct)
        is_correct = (
            selected_index is not None
            and 0 <= correct_index < len(options)
            and selected_index == correct_index
        )
        selected_label = ''
        if selected_index is not None and 0 <= selected_index < len(options):
            selected_label = options[selected_index]
        breakdown.append({
            'id': question.pk,
            'question': question.question,
            'answer_options': options,
            'selected_index': selected_index,
            'selected_label': selected_label,
            'correct_index': correct_index if 0 <= correct_index < len(options) else None,
            'correct_label': options[correct_index] if 0 <= correct_index < len(options) else question.correct_answer,
            'is_correct': is_correct,
        })
    return breakdown


def _serialize_score_detail(row: QuizResult, *, role: str) -> dict:
    from portals.utils.quiz_submit import build_essay_question_responses

    quiz = row.quiz
    if quiz.is_reading:
        from portals.utils.quiz_reading import get_reading_questions_for_quiz

        question_count = len(get_reading_questions_for_quiz(quiz))
    elif quiz.is_speaking:
        from portals.utils.quiz_speaking import get_speaking_questions_for_quiz

        question_count = len(get_speaking_questions_for_quiz(quiz))
    elif quiz.is_listening:
        from portals.utils.quiz_listening import get_listening_questions_for_quiz

        question_count = len(get_listening_questions_for_quiz(quiz))
    else:
        question_count = quiz.questions.count()
    max_value = quiz.score_max_value(question_count=question_count)
    back_routes = {
        'teacher': 'portals:teacher-notifications',
        'parent': 'portals:parent-notifications',
        'student': 'portals:student-notifications',
    }
    latest_review = row.reviews.select_related('reviewer__user').first()
    completion_trigger = getattr(row, 'completion_trigger', 'manual') or 'manual'
    trigger_labels = dict(QuizResult.CompletionTrigger.choices)
    data = {
        'id': row.pk,
        'student_name': row.student.full_name,
        'quiz_topic': quiz.topic,
        'grading_mode_label': quiz.get_grading_mode_label(),
        'is_manual_grading': quiz.is_manual_grading,
        'is_essay': quiz.is_essay,
        'total_score': row.total_score,
        'max_value': max_value,
        'duration_sec': row.duration_sec,
        'is_time_limited': bool(quiz.is_time_limited and quiz.time_limit_minutes),
        'time_limit_minutes': quiz.time_limit_minutes,
        'time_limit_seconds': quiz.time_limit_seconds or 0,
        'completion_trigger': completion_trigger,
        'completion_trigger_label': trigger_labels.get(completion_trigger, completion_trigger),
        'timed_out': completion_trigger == QuizResult.CompletionTrigger.TIME_LIMIT,
        'completed_at': row.completed_at,
        'reviewed_at': row.reviewed_at,
        'student_submission': row.student_submission,
        'teacher_feedback': row.teacher_feedback,
        'reviewer_name': latest_review.reviewer.full_name if latest_review else '',
        'back_url': reverse(back_routes[role]),
    }
    if quiz.is_variant_quiz:
        data['breakdown'] = _build_variant_breakdown(row)
    elif quiz.is_reading:
        from portals.utils.quiz_reading import build_reading_sections_for_quiz

        response_map = {
            str(key): str(value)
            for key, value in (row.given_answers or {}).items()
        }
        teacher_correct_map = {
            str(key): str(value)
            for key, value in (row.teacher_correct_answers or {}).items()
            if str(value).strip()
        }
        data['is_reading'] = True
        data['reading_sections'] = build_reading_sections_for_quiz(
            quiz.pk,
            response_map=response_map,
            correct_answer_map=teacher_correct_map or None,
            use_admin_answer_keys=not teacher_correct_map,
        )
        data['breakdown'] = [
            {
                'id': item['id'],
                'question': item.get('question', ''),
                'question_type_label': item.get('question_type_label', ''),
                'student_answer': item.get('student_answer_display', ''),
                'correct_answer': item.get('correct_answer_display', item.get('correct_answer', '')),
                'is_correct': item.get('is_correct'),
            }
            for section in data['reading_sections']
            for item in section['questions']
        ]
    elif quiz.is_listening:
        from portals.utils.quiz_listening import build_listening_sections_for_quiz

        response_map = {
            str(key): str(value)
            for key, value in (row.given_answers or {}).items()
        }
        data['is_listening'] = True
        data['listening_sections'] = build_listening_sections_for_quiz(
            quiz.pk,
            response_map=response_map,
            use_admin_answer_keys=True,
        )
        data['question_responses'] = build_essay_question_responses(row)
    elif quiz.is_speaking:
        from portals.models import SpeakingRecording
        from portals.utils.quiz_speaking import (
            build_speaking_sections_for_quiz,
            estimate_speaking_quiz_seconds,
        )

        recording_map = {
            str(recording.question_id): {
                'audio_url': recording.audio_url,
                'duration_sec': recording.duration_sec,
            }
            for recording in SpeakingRecording.objects.filter(result_id=row.pk).select_related('question')
        }
        sections = build_speaking_sections_for_quiz(
            quiz.pk,
            recording_map=recording_map,
        )
        data['is_speaking'] = True
        data['speaking_sections'] = sections
        estimated_total_seconds = estimate_speaking_quiz_seconds(sections)
        data['estimated_total_seconds'] = estimated_total_seconds
        data['estimated_total_minutes'] = max(1, round(estimated_total_seconds / 60))
        data['question_responses'] = build_essay_question_responses(row)
    elif quiz.is_essay or quiz.uses_per_question_text_responses:
        data['question_responses'] = build_essay_question_responses(row)
        data['questions'] = [serialize_quiz_question(q) for q in quiz.questions.all()]
    else:
        data['questions'] = [serialize_quiz_question(q) for q in quiz.questions.all()]
    return data


def get_score_detail_for_teacher(teacher_id: int, result_id: int) -> dict | None:
    row = (
        QuizResult.objects.filter(pk=result_id)
        .select_related('student__user', 'quiz__category')
        .prefetch_related(
            Prefetch('quiz__questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
            Prefetch('reviews', queryset=QuizResultReview.objects.select_related('reviewer__user')),
        )
        .first()
    )
    if not row:
        return None
    if row.quiz.is_manual_grading and row.is_pending_review:
        if not teacher_can_see_quiz_result(teacher_id, row.student_id, row.quiz):
            return None
    elif not is_quiz_result_published(row) or not teacher_can_see_quiz_result(teacher_id, row.student_id, row.quiz):
        return None
    return _serialize_score_detail(row, role='teacher')


def get_score_detail_for_parent(parent_id: int, result_id: int) -> dict | None:
    row = (
        QuizResult.objects.filter(pk=result_id)
        .select_related('student__user', 'quiz__category')
        .prefetch_related(
            Prefetch('quiz__questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
            Prefetch('reviews', queryset=QuizResultReview.objects.select_related('reviewer__user')),
        )
        .first()
    )
    if not row or not parent_can_view_quiz_result(parent_id, row):
        return None
    return _serialize_score_detail(row, role='parent')


def get_score_detail_for_student(student_id: int, result_id: int) -> dict | None:
    row = (
        QuizResult.objects.filter(pk=result_id)
        .select_related('student__user', 'quiz__category')
        .prefetch_related(
            Prefetch('quiz__questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
        )
        .first()
    )
    if not row or not student_can_view_quiz_result(student_id, row):
        return None
    return _serialize_score_detail(row, role='student')

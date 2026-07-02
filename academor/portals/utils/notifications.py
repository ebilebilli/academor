"""Portal quiz score notifications for teachers, parents, and students."""

from __future__ import annotations

from datetime import timedelta

from django.db.models import Prefetch
from django.urls import reverse
from django.utils import timezone

from portals.models import (
    ParentProfile,
    PortalNotification,
    QuizQuestion,
    QuizResult,
    QuizResultReview,
    StudyGroup,
)
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
    """Score published — notify parents and optionally teachers; students only for manual quizzes."""
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


def dismiss_teacher_submission_notifications(result: QuizResult, *, teacher_id: int | None = None) -> None:
    qs = PortalNotification.objects.filter(
        quiz_result=result,
        kind=PortalNotification.Kind.SUBMISSION_PENDING,
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
    qs = (
        PortalNotification.objects.select_related(
            'quiz_result__student__user',
            'quiz_result__quiz__category',
        )
        .order_by('-created_at', '-id')
    )
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


def get_teacher_pending_review_count(teacher_id: int) -> int:
    from portals.utils.queries import _teacher_pending_quiz_results_queryset
    from portals.utils.student_courses import filter_quiz_results_for_teacher

    qs = _teacher_pending_quiz_results_queryset(teacher_id)
    if qs is None:
        return 0
    return len(filter_quiz_results_for_teacher(qs[:100], teacher_id))


def get_teacher_portal_bell_count(teacher_id: int) -> int:
    """Unread published-result notifications for teachers (not pending manual reviews)."""
    return _notification_queryset(
        teacher_id=teacher_id,
        teacher_kind=PortalNotification.Kind.RESULT_PUBLISHED,
    ).filter(is_read=False).count()


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
    result = row.quiz_result
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
    elif parent_id:
        role = 'parent'
    else:
        role = 'student'
    qs = _apply_period_filter(
        _notification_queryset(
            teacher_id=teacher_id,
            parent_id=parent_id,
            student_id=student_id,
            teacher_kind=PortalNotification.Kind.RESULT_PUBLISHED,
        ),
        period,
    )
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
        )
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

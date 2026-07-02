"""Score and persist student quiz attempts."""

from __future__ import annotations

from django.db import IntegrityError
from django.db.models import Prefetch
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext as _

from portals.models import Quiz, QuizQuestion, QuizResult

_COMPLETION_TRIGGERS = {
    value for value, _label in QuizResult.CompletionTrigger.choices
}
from portals.utils.student_courses import quiz_visible_to_student
from portals.utils.quiz_listening import get_listening_questions_for_quiz


def student_has_quiz_attempt(student_id: int, quiz_id: int) -> bool:
    return QuizResult.objects.filter(student_id=student_id, quiz_id=quiz_id).exists()


def student_can_take_manual_quiz(student_id: int, quiz_id: int) -> bool:
    """First attempt, or a new attempt after the teacher has published a review."""
    result = QuizResult.objects.filter(student_id=student_id, quiz_id=quiz_id).first()
    if not result:
        return True
    if result.is_pending_review:
        return False
    return result.reviewed_at is not None


def get_student_quiz_attempt_map(student_id: int, quiz_ids: list[int] | None = None) -> dict[int, int]:
    qs = QuizResult.objects.filter(student_id=student_id)
    if quiz_ids:
        qs = qs.filter(quiz_id__in=quiz_ids)
    return dict(qs.values_list('quiz_id', 'pk'))


def get_student_quiz_attempt_meta(student_id: int, quiz_ids: list[int] | None = None) -> dict[int, dict]:
    qs = QuizResult.objects.filter(student_id=student_id)
    if quiz_ids:
        qs = qs.filter(quiz_id__in=quiz_ids)
    return {
        row['quiz_id']: {
            'result_id': row['pk'],
            'is_reviewed': row['reviewed_at'] is not None,
            'is_pending_review': row['reviewed_at'] is None,
        }
        for row in qs.values('quiz_id', 'pk', 'reviewed_at')
    }


def _question_correct_index(question) -> int | None:
    options = question.answer_options or []
    correct = (question.correct_answer or '').strip()
    if correct and correct in options:
        return options.index(correct)
    index = question.correct_option_index
    if 0 <= index < len(options):
        return index
    return None


def _normalize_given_answers(raw: dict) -> dict[int, int | None]:
    normalized = {}
    if not isinstance(raw, dict):
        return normalized
    for key, value in raw.items():
        try:
            question_id = int(key)
        except (TypeError, ValueError):
            continue
        if value is None or value == '':
            normalized[question_id] = None
            continue
        try:
            normalized[question_id] = int(value)
        except (TypeError, ValueError):
            normalized[question_id] = None
    return normalized


def _normalize_completion_trigger(raw) -> str:
    value = str(raw or QuizResult.CompletionTrigger.MANUAL).strip()
    if value in _COMPLETION_TRIGGERS:
        return value
    return QuizResult.CompletionTrigger.MANUAL


def _resolve_duration_sec(
    quiz: Quiz,
    *,
    client_duration_sec: int,
    session_started_at: str | None,
    require_session: bool = False,
) -> tuple[int | None, str | None]:
    if quiz.is_time_limited and quiz.time_limit_minutes and require_session and not session_started_at:
        return None, str(_('Quiz session expired. Open the quiz again and finish within the time limit.'))

    duration = max(0, int(client_duration_sec or 0))
    if session_started_at:
        parsed = parse_datetime(session_started_at)
        if parsed:
            if timezone.is_naive(parsed):
                parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
            elapsed = int((timezone.now() - parsed).total_seconds())
            if elapsed >= 0:
                duration = elapsed
    elif quiz.is_time_limited and quiz.time_limit_minutes:
        return None, str(_('Quiz session expired. Open the quiz again and finish within the time limit.'))

    if quiz.is_time_limited and quiz.time_limit_minutes:
        cap = int(quiz.time_limit_minutes) * 60
        if duration > cap + 5:
            return None, str(_('Time limit exceeded.'))
        duration = min(duration, cap)
    return duration, None


def _load_quiz_for_student(student_id: int, quiz_id: int) -> Quiz | None:
    quiz = (
        Quiz.objects.filter(pk=quiz_id)
        .select_related('category')
        .prefetch_related(
            Prefetch(
                'questions',
                queryset=QuizQuestion.objects.order_by('order', 'id'),
            ),
        )
        .first()
    )
    if not quiz or not quiz_visible_to_student(quiz, student_id):
        return None
    return quiz


def _answerable_questions(quiz: Quiz) -> list[QuizQuestion]:
    return [question for question in quiz.questions.all() if question.is_answerable]


def _question_variant_options(question) -> list[str]:
    options = getattr(question, 'variant_options', None)
    if callable(options):
        options = options()
    elif options is not None:
        options = list(options)
    else:
        options = getattr(question, 'answer_options', None) or []
    return [str(item).strip() for item in options if str(item).strip()]


def _looks_like_variant_index(value, question=None) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        if question is None:
            return True
        options = _question_variant_options(question)
        return len(options) >= 2 and 0 <= value < len(options)
    text = str(value or '').strip()
    if not text.isdigit():
        return False
    if question is None:
        return False
    options = _question_variant_options(question)
    if len(options) < 2:
        return False
    index = int(text)
    return 0 <= index < len(options)


def _listening_question_is_variant(question) -> bool:
    options = getattr(question, 'variant_options', None)
    if callable(options):
        options = options()
    elif options is None:
        options = [str(item).strip() for item in (getattr(question, 'answer_options', None) or []) if str(item).strip()]
    return len(options) >= 2


def listening_student_answer_display(question, raw_value) -> str:
    if raw_value is None or raw_value == '':
        return ''
    options = getattr(question, 'variant_options', None)
    if callable(options):
        options = options()
    elif options is None:
        options = [str(item).strip() for item in (getattr(question, 'answer_options', None) or []) if str(item).strip()]
    if len(options) >= 2 and _looks_like_variant_index(raw_value, question):
        return options[int(raw_value)]
    return str(raw_value).strip()


def _normalize_essay_text_answers(
    raw: dict | None,
    quiz: Quiz,
    *,
    ordered_answers: list | None = None,
) -> dict[str, str]:
    questions = _answerable_questions(quiz)
    question_ids = {question.pk for question in questions}
    normalized: dict[str, str] = {}
    fallback_values: list[str] = []

    if isinstance(raw, dict):
        question_by_id = {question.pk: question for question in questions}
        for key, value in raw.items():
            text = str(value or '').strip()
            try:
                question_id = int(key)
            except (TypeError, ValueError):
                if text:
                    fallback_values.append(text)
                continue
            if question_id not in question_ids:
                if text:
                    fallback_values.append(text)
                continue
            if _looks_like_variant_index(value, question_by_id.get(question_id)):
                continue
            if text:
                normalized[str(question_id)] = text

    if len(normalized) < len(questions) and fallback_values:
        if len(fallback_values) == len(questions):
            for question, value in zip(questions, fallback_values):
                normalized[str(question.pk)] = value

    if len(normalized) < len(questions) and ordered_answers is not None:
        values = [str(value or '').strip() for value in ordered_answers]
        if len(values) == len(questions) and all(values):
            for question, value in zip(questions, values):
                normalized[str(question.pk)] = value

    return normalized


def _student_answer_display(question: QuizQuestion, raw_value) -> str:
    if raw_value is None or raw_value == '':
        return ''
    options = question.answer_options or []
    if options and _looks_like_variant_index(raw_value, question):
        index = int(raw_value)
        if 0 <= index < len(options):
            return options[index]
    return str(raw_value).strip()


def _normalize_listening_model_answers(
    raw: dict | None,
    quiz: Quiz,
    *,
    ordered_answers: list | None = None,
) -> dict[str, str]:
    questions = get_listening_questions_for_quiz(quiz)
    question_by_id = {question.pk: question for question in questions}
    question_ids = set(question_by_id)
    normalized: dict[str, str] = {}
    fallback_values: list[str] = []

    if isinstance(raw, dict):
        for key, value in raw.items():
            try:
                question_id = int(key)
            except (TypeError, ValueError):
                text = '' if value is None else str(value).strip()
                if text:
                    fallback_values.append(text)
                continue
            if question_id not in question_ids:
                text = '' if value is None else str(value).strip()
                if text:
                    fallback_values.append(text)
                continue
            question = question_by_id[question_id]
            if _listening_question_is_variant(question):
                if _looks_like_variant_index(value, question):
                    normalized[str(question_id)] = str(int(value))
                continue
            text = '' if value is None else str(value).strip()
            if text:
                normalized[str(question_id)] = text

    if len(normalized) < len(questions) and fallback_values:
        if len(fallback_values) == len(questions):
            for question, value in zip(questions, fallback_values):
                if str(question.pk) in normalized:
                    continue
                if _listening_question_is_variant(question):
                    if _looks_like_variant_index(value, question):
                        normalized[str(question.pk)] = str(int(value))
                else:
                    text = '' if value is None else str(value).strip()
                    if text:
                        normalized[str(question.pk)] = text

    if len(normalized) < len(questions) and ordered_answers is not None:
        values = list(ordered_answers)
        if len(values) == len(questions):
            for question, value in zip(questions, values):
                if str(question.pk) in normalized:
                    continue
                if _listening_question_is_variant(question):
                    if _looks_like_variant_index(value, question):
                        normalized[str(question.pk)] = str(int(value))
                else:
                    text = '' if value is None else str(value).strip()
                    if text:
                        normalized[str(question.pk)] = text

    return normalized


def _validate_listening_model_answers(quiz: Quiz, answers: dict[str, str]) -> str | None:
    questions = get_listening_questions_for_quiz(quiz)
    if not questions:
        return str(_('No listening questions found for this category.'))
    missing = []
    for question in questions:
        raw = answers.get(str(question.pk), '')
        if _listening_question_is_variant(question):
            if not _looks_like_variant_index(raw, question):
                missing.append(question.pk)
        elif not str(raw).strip():
            missing.append(question.pk)
    if missing:
        return str(_('Answer every task before submitting.'))
    return None


def _validate_essay_text_answers(quiz: Quiz, answers: dict[str, str]) -> str | None:
    questions = _answerable_questions(quiz)
    if not questions:
        return str(_('No questions found.'))
    missing_question_ids = [
        question.pk
        for question in questions
        if not answers.get(str(question.pk), '').strip()
    ]
    if missing_question_ids:
        return str(_('Answer every task before submitting.'))
    return None


def build_essay_question_responses(result: QuizResult) -> list[dict]:
    quiz = result.quiz
    given = result.given_answers or {}
    if quiz.is_listening:
        questions = get_listening_questions_for_quiz(quiz)
        responses = []
        for index, question in enumerate(questions, start=1):
            raw = given.get(str(question.pk), given.get(question.pk, ''))
            responses.append({
                'id': question.pk,
                'number': index,
                'question': question.question,
                'prompt_type': 'variant' if _listening_question_is_variant(question) else 'text',
                'student_answer': listening_student_answer_display(question, raw),
            })
        return responses

    questions = _answerable_questions(quiz)
    responses = []
    legacy_submission = (result.student_submission or '').strip()

    for index, question in enumerate(questions, start=1):
        raw = given.get(str(question.pk), given.get(question.pk, ''))
        answer = _student_answer_display(question, raw)
        if not answer and len(questions) == 1 and legacy_submission:
            answer = legacy_submission
        responses.append({
            'id': question.pk,
            'number': index,
            'question': question.question,
            'prompt_type': question.prompt_type,
            'student_answer': answer,
        })
    return responses


def score_variant_quiz(
    quiz: Quiz,
    given_answers: dict,
) -> tuple[float, int, list[dict]]:
    answers = _normalize_given_answers(given_answers)
    questions = list(
        quiz.questions.order_by('order', 'id').only(
            'id', 'answer_options', 'correct_answer', 'correct_option_index',
        ),
    )
    max_score = len(questions)
    score = 0.0
    breakdown = []

    for question in questions:
        correct_index = _question_correct_index(question)
        selected_index = answers.get(question.pk)
        is_correct = (
            correct_index is not None
            and selected_index is not None
            and selected_index == correct_index
        )
        if is_correct:
            score += 1.0
        breakdown.append({
            'id': question.pk,
            'selected_index': selected_index,
            'correct_index': correct_index,
            'is_correct': is_correct,
        })

    return score, max_score, breakdown


def submit_variant_quiz_attempt(
    *,
    student_id: int,
    quiz_id: int,
    given_answers: dict,
    duration_sec: int = 0,
    session_started_at: str | None = None,
    completion_trigger: str = QuizResult.CompletionTrigger.MANUAL,
) -> dict:
    quiz = _load_quiz_for_student(student_id, quiz_id)
    if not quiz:
        return {'success': False, 'error': _('Quiz not found.')}
    if not quiz.is_variant_quiz:
        return {'success': False, 'error': _('This quiz cannot be submitted automatically.')}

    if not quiz.questions.exists():
        return {'success': False, 'error': _('This quiz has no questions yet.')}

    resolved_duration, duration_error = _resolve_duration_sec(
        quiz,
        client_duration_sec=duration_sec,
        session_started_at=session_started_at,
        require_session=bool(quiz.is_time_limited and quiz.time_limit_minutes),
    )
    if duration_error:
        return {'success': False, 'error': duration_error}

    resolved_trigger = _normalize_completion_trigger(completion_trigger)
    score, max_score, breakdown = score_variant_quiz(quiz, given_answers)
    stored_answers = {
        str(item['id']): item['selected_index']
        for item in breakdown
        if item['selected_index'] is not None
    }

    now = timezone.now()
    existing = QuizResult.objects.filter(student_id=student_id, quiz_id=quiz_id).first()
    if existing:
        existing.given_answers = stored_answers
        existing.total_score = score
        existing.duration_sec = resolved_duration or 0
        existing.completion_trigger = resolved_trigger
        existing.completed_at = now
        existing.save(update_fields=[
            'given_answers', 'total_score', 'duration_sec', 'completion_trigger', 'completed_at',
        ])
        result = existing
    else:
        try:
            result = QuizResult.objects.create(
                student_id=student_id,
                quiz=quiz,
                given_answers=stored_answers,
                total_score=score,
                duration_sec=resolved_duration or 0,
                completion_trigger=resolved_trigger,
            )
        except IntegrityError:
            existing = QuizResult.objects.filter(student_id=student_id, quiz_id=quiz_id).first()
            if not existing:
                return {'success': False, 'error': _('Could not save the quiz result.')}
            existing.given_answers = stored_answers
            existing.total_score = score
            existing.duration_sec = resolved_duration or 0
            existing.completion_trigger = resolved_trigger
            existing.completed_at = now
            existing.save(update_fields=[
                'given_answers', 'total_score', 'duration_sec', 'completion_trigger', 'completed_at',
            ])
            result = existing

    from portals.utils.notifications import create_published_result_notifications

    create_published_result_notifications(
        QuizResult.objects.select_related('quiz__category', 'student').get(pk=result.pk),
    )

    percent = round(100 * score / max_score, 1) if max_score else 0.0

    return {
        'success': True,
        'result_id': result.pk,
        'total_score': score,
        'max_score': max_score,
        'percent': percent,
        'duration_sec': resolved_duration or 0,
        'completion_trigger': resolved_trigger,
        'questions': breakdown,
        'breakdown': breakdown,
    }


def submit_manual_quiz_attempt(
    *,
    student_id: int,
    quiz_id: int,
    student_submission: str = '',
    given_answers: dict | None = None,
    ordered_answers: list | None = None,
    duration_sec: int = 0,
    session_started_at: str | None = None,
    allow_empty_submission: bool = False,
    completion_trigger: str = QuizResult.CompletionTrigger.MANUAL,
) -> dict:
    quiz = _load_quiz_for_student(student_id, quiz_id)
    if not quiz:
        return {'success': False, 'error': _('Quiz not found.')}
    if not quiz.is_manual_grading:
        return {'success': False, 'error': _('This quiz is not a manual-review task.')}

    submission = (student_submission or '').strip()
    text_answers: dict[str, str] = {}
    listening_answers: dict[str, str] = {}
    uses_text_responses = quiz.uses_per_question_text_responses
    answerable_questions = _answerable_questions(quiz)
    if quiz.is_listening:
        listening_answers = _normalize_listening_model_answers(
            given_answers,
            quiz,
            ordered_answers=ordered_answers,
        )
        if not allow_empty_submission:
            validation_error = _validate_listening_model_answers(quiz, listening_answers)
            if validation_error:
                return {'success': False, 'error': validation_error}
    elif uses_text_responses:
        text_answers = _normalize_essay_text_answers(
            given_answers,
            quiz,
            ordered_answers=ordered_answers,
        )
        if not text_answers and submission:
            if len(answerable_questions) == 1:
                text_answers = {str(answerable_questions[0].pk): submission}
        if not allow_empty_submission:
            validation_error = _validate_essay_text_answers(quiz, text_answers)
            if validation_error:
                return {'success': False, 'error': validation_error}
    elif not submission and not allow_empty_submission:
        return {'success': False, 'error': _('Enter your answer before submitting.')}

    existing = QuizResult.objects.filter(student_id=student_id, quiz_id=quiz_id).first()
    if existing and existing.is_pending_review:
        return {'success': False, 'error': _('Your submission is awaiting teacher review.')}

    resolved_duration, duration_error = _resolve_duration_sec(
        quiz,
        client_duration_sec=duration_sec,
        session_started_at=session_started_at,
        require_session=bool(quiz.is_time_limited and quiz.time_limit_minutes),
    )
    if duration_error:
        return {'success': False, 'error': duration_error}

    resolved_trigger = _normalize_completion_trigger(completion_trigger)

    def apply_submission_fields(result_obj: QuizResult) -> None:
        result_obj.duration_sec = resolved_duration or 0
        result_obj.completion_trigger = resolved_trigger
        result_obj.completed_at = timezone.now()
        if quiz.is_listening:
            result_obj.given_answers = listening_answers
            result_obj.student_submission = ''
        elif uses_text_responses:
            result_obj.given_answers = text_answers
            result_obj.student_submission = ''
        else:
            result_obj.student_submission = submission
            result_obj.given_answers = {}

    def reset_review_fields(result_obj: QuizResult) -> list[str]:
        from portals.utils.notifications import clear_published_result_notifications

        clear_published_result_notifications(result_obj)
        result_obj.reviewed_at = None
        result_obj.total_score = None
        result_obj.teacher_feedback = ''
        return ['reviewed_at', 'total_score', 'teacher_feedback']

    if existing:
        apply_submission_fields(existing)
        if existing.reviewed_at is not None:
            existing.save(update_fields=[
                'given_answers',
                'student_submission',
                'duration_sec',
                'completion_trigger',
                'completed_at',
                *reset_review_fields(existing),
            ])
        else:
            existing.save(update_fields=[
                'given_answers',
                'student_submission',
                'duration_sec',
                'completion_trigger',
                'completed_at',
            ])
        result = existing
    else:
        try:
            create_kwargs = {
                'student_id': student_id,
                'quiz': quiz,
                'duration_sec': resolved_duration or 0,
                'completion_trigger': resolved_trigger,
            }
            if quiz.is_listening:
                create_kwargs['given_answers'] = listening_answers
                create_kwargs['student_submission'] = ''
            elif uses_text_responses:
                create_kwargs['given_answers'] = text_answers
                create_kwargs['student_submission'] = ''
            else:
                create_kwargs['student_submission'] = submission
                create_kwargs['given_answers'] = {}
            result = QuizResult.objects.create(**create_kwargs)
        except IntegrityError:
            existing = QuizResult.objects.filter(student_id=student_id, quiz_id=quiz_id).first()
            if not existing:
                return {'success': False, 'error': _('Could not save the submission.')}
            if existing.is_pending_review:
                return {'success': False, 'error': _('Your submission is awaiting teacher review.')}
            apply_submission_fields(existing)
            if existing.reviewed_at is not None:
                existing.save(update_fields=[
                    'given_answers',
                    'student_submission',
                    'duration_sec',
                    'completion_trigger',
                    'completed_at',
                    *reset_review_fields(existing),
                ])
            else:
                existing.save(update_fields=[
                    'given_answers',
                    'student_submission',
                    'duration_sec',
                    'completion_trigger',
                    'completed_at',
                ])
            result = existing

    from portals.utils.cache_utils import invalidate_model_cache
    from portals.utils.notifications import (
        create_student_submission_notification,
        create_teacher_submission_notifications,
    )

    result_with_relations = QuizResult.objects.select_related('quiz__category', 'student').get(pk=result.pk)
    create_teacher_submission_notifications(result_with_relations)
    create_student_submission_notification(result_with_relations)

    invalidate_model_cache('QuizResult')

    return {
        'success': True,
        'result_id': result.pk,
        'duration_sec': resolved_duration or 0,
        'completion_trigger': resolved_trigger,
    }


def submit_teacher_quiz_review(
    *,
    teacher_id: int,
    result_id: int,
    total_score,
    teacher_feedback: str = '',
) -> dict:
    from portals.models import QuizResultReview
    from portals.utils.cache_utils import invalidate_model_cache
    from portals.utils.notifications import (
        create_published_result_notifications,
        dismiss_teacher_submission_notifications,
    )
    from portals.utils.student_courses import teacher_can_see_quiz_result

    result = (
        QuizResult.objects.select_related('quiz__category', 'student')
        .filter(pk=result_id)
        .first()
    )
    if not result or not result.quiz.is_manual_grading:
        return {'success': False, 'error': _('Result not found.')}
    if not teacher_can_see_quiz_result(teacher_id, result.student_id, result.quiz):
        return {'success': False, 'error': _('Result not found.')}
    if result.reviewed_at is not None:
        return {'success': False, 'error': _('This submission has already been reviewed.')}

    try:
        score_value = round(float(total_score), 2)
    except (TypeError, ValueError):
        return {'success': False, 'error': _('Enter a valid score.')}

    max_score = result.quiz.MANUAL_REVIEW_MAX_SCORE
    if score_value < 0 or score_value > max_score:
        return {
            'success': False,
            'error': _('Score must be between 0 and %(max)s.') % {'max': max_score},
        }

    result.total_score = score_value
    result.teacher_feedback = (teacher_feedback or '').strip()
    result.reviewed_at = timezone.now()
    result.save(update_fields=['total_score', 'teacher_feedback', 'reviewed_at'])

    QuizResultReview.objects.create(
        result=result,
        reviewer_id=teacher_id,
        score=score_value,
        feedback=result.teacher_feedback,
    )

    dismiss_teacher_submission_notifications(result, teacher_id=teacher_id)
    create_published_result_notifications(
        result,
        exclude_teacher_id=teacher_id,
        notify_teachers=True,
    )

    invalidate_model_cache('QuizResult')

    return {'success': True, 'result_id': result.pk}


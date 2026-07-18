"""Quiz portal queries and serializers."""
from django.db.models import Count, Prefetch, Q

from portals.models import Quiz, QuizCategory, QuizQuestion, QuizResult, Score
from portals.utils.quiz_category_services import (
    category_has_portal_code,
    quiz_categories_for_portal_codes,
    quiz_category_primary_portal_code,
    quiz_category_slugs_for_portal_codes,
)
from portals.utils.student_courses import get_student_course_type_codes
from portals.utils.teacher_courses import get_teacher_course_type_codes


def serialize_quiz(quiz):
    from portals.utils.portal_services import resolve_course_type_label
    from portals.utils.student_courses import get_quiz_service_code

    code = get_quiz_service_code(quiz)
    label = resolve_course_type_label(code) if code else ''
    category = getattr(quiz, 'category', None)
    inline_count = quiz.questions.count() if hasattr(quiz, 'questions') else 0
    question_count = inline_count
    return {
        'id': quiz.pk,
        'topic': quiz.topic,
        'course_type': code,
        'course_types': [code] if code else [],
        'course_type_label': label,
        'category_id': quiz.category_id,
        'category_name': category.name if category else '',
        'created_at': quiz.created_at,
        'question_count': question_count,
        'is_listening': quiz.is_listening,
        'is_essay': quiz.is_essay,
        'is_speaking': quiz.is_speaking,
        'is_manual_grading': quiz.is_manual_grading,
        'uses_per_question_text_responses': quiz.uses_per_question_text_responses,
        'is_variant_quiz': quiz.is_variant_quiz,
        'grading_mode': quiz.grading_mode,
        'grading_mode_label': quiz.get_grading_mode_label(),
        'is_time_limited': quiz.is_time_limited,
        'time_limit_minutes': quiz.time_limit_minutes,
        'time_limit_seconds': quiz.time_limit_seconds,
    }


def serialize_quiz_category(category):
    from portals.utils.portal_services import resolve_course_type_label

    quiz_count = getattr(category, 'quiz_count', None)
    if quiz_count is None:
        quiz_count = category.quizzes.count()
    service_code = quiz_category_primary_portal_code(category)
    return {
        'id': category.pk,
        'name': category.name,
        'service': service_code,
        'service_label': resolve_course_type_label(service_code, lang='en') if service_code else '',
        'quiz_count': quiz_count,
    }


def build_quiz_service_tabs(categories):
    from django.utils.translation import gettext as _

    from portals.utils.portal_services import get_course_type_label_map

    labels = get_course_type_label_map(lang='en')
    counts = {}
    for category in categories:
        code = category.get('service') or ''
        if code:
            counts[code] = counts.get(code, 0) + 1
    tabs = [{
        'code': 'all',
        'label': _('All services'),
        'count': len(categories),
    }]
    for code in sorted(counts):
        tabs.append({
            'code': code,
            'label': labels.get(code, code),
            'count': counts[code],
        })
    return tabs


def teacher_can_access_quiz_category(teacher_id, category_id):
    row = QuizCategory.objects.filter(pk=category_id).prefetch_related('services').first()
    if not row:
        return False
    return category_has_portal_code(row, get_teacher_course_type_codes(teacher_id))


def student_can_access_quiz_category(student_id, category_id):
    row = QuizCategory.objects.filter(pk=category_id).prefetch_related('services').first()
    if not row:
        return False
    return category_has_portal_code(row, get_student_course_type_codes(student_id))


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_quiz_categories(teacher_id):
    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return []
    qs = quiz_categories_for_portal_codes(course_codes).order_by('name', 'id')
    result = []
    for category in qs:
        visible = get_teacher_quizzes_for_category(teacher_id, category.pk)
        if not visible:
            continue
        data = serialize_quiz_category(category)
        data['quiz_count'] = len(visible)
        result.append(data)
    return result


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_quiz_categories(student_id):
    course_codes = get_student_course_type_codes(student_id)
    if not course_codes:
        return []
    qs = quiz_categories_for_portal_codes(course_codes).order_by('name', 'id')
    result = []
    for category in qs:
        visible = get_student_quizzes_for_category(student_id, category.pk)
        if not visible:
            continue
        data = serialize_quiz_category(category)
        data['quiz_count'] = len(visible)
        result.append(data)
    return result


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_quiz_category(teacher_id, category_id):
    if not teacher_can_access_quiz_category(teacher_id, category_id):
        return None
    row = QuizCategory.objects.filter(pk=category_id).first()
    if not row:
        return None
    visible = get_teacher_quizzes_for_category(teacher_id, category_id)
    if not visible:
        return None
    data = serialize_quiz_category(row)
    data['quiz_count'] = len(visible)
    return data


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_quiz_category(student_id, category_id):
    if not student_can_access_quiz_category(student_id, category_id):
        return None
    row = QuizCategory.objects.filter(pk=category_id).first()
    if not row:
        return None
    visible = get_student_quizzes_for_category(student_id, category_id)
    if not visible:
        return None
    data = serialize_quiz_category(row)
    data['quiz_count'] = len(visible)
    return data


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_quizzes_for_category(teacher_id, category_id):
    from portals.utils.student_courses import quiz_visible_to_teacher

    if not teacher_can_access_quiz_category(teacher_id, category_id):
        return []
    course_codes = get_teacher_course_type_codes(teacher_id)
    qs = (
        Quiz.objects.filter(
            category_id=category_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related('questions')
        .distinct()
        .order_by('-created_at', 'id')
    )
    visible = [row for row in qs if quiz_visible_to_teacher(row, teacher_id)]
    return [serialize_quiz(row) for row in visible]


def _attach_quiz_attempt_flags(student_id, quizzes):
    from portals.utils.quiz_submit import get_student_quiz_attempt_meta

    if not quizzes:
        return quizzes
    attempt_meta = get_student_quiz_attempt_meta(student_id, [row['id'] for row in quizzes])
    enriched = []
    for row in quizzes:
        meta = attempt_meta.get(row['id'], {})
        has_attempt = row['id'] in attempt_meta
        is_reviewed = bool(meta.get('is_reviewed'))
        is_pending_review = has_attempt and bool(meta.get('is_pending_review'))
        enriched.append({
            **row,
            'has_attempt': has_attempt,
            'result_id': meta.get('result_id'),
            'is_reviewed': is_reviewed,
            'is_pending_review': is_pending_review,
            'can_take_manual_quiz': (
                not row.get('is_manual_grading') or not has_attempt or is_reviewed
            ),
        })
    return enriched


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_quizzes_for_category(student_id, category_id):
    # Keep locked quizzes visible with is_locked flags (same as portals.utils.queries).
    from portals.utils.quiz_assignments import get_student_quiz_assignment_map
    from portals.utils.student_courses import student_quiz_enrollment_ok

    if not student_can_access_quiz_category(student_id, category_id):
        return []
    course_codes = get_student_course_type_codes(student_id)
    qs = (
        Quiz.objects.filter(
            category_id=category_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related('questions')
        .distinct()
        .order_by('-created_at', 'id')
    )
    enrolled = [row for row in qs if student_quiz_enrollment_ok(student_id, row)]
    assignment_map = get_student_quiz_assignment_map(
        student_id,
        [row.pk for row in enrolled],
    )
    quizzes = []
    for row in enrolled:
        data = serialize_quiz(row)
        is_unlocked = bool(assignment_map.get(row.pk, False))
        data['is_unlocked'] = is_unlocked
        data['is_locked'] = not is_unlocked
        quizzes.append(data)
    return _attach_quiz_attempt_flags(student_id, quizzes)


def _quiz_correct_option_letter(question):
    options = question.answer_options or []
    correct = (question.correct_answer or '').strip()
    if correct and correct in options:
        return chr(97 + options.index(correct))
    index = question.correct_option_index
    if 0 <= index < len(options):
        return chr(97 + index)
    return ''


def serialize_quiz_question_for_student(question, *, student_answer: str = ''):
    media_file_url = ''
    if question.media_file:
        try:
            media_file_url = question.media_file.url
        except ValueError:
            media_file_url = ''

    return {
        'id': question.pk,
        'quiz_id': getattr(question, 'quiz_id', None),
        'prompt_type': question.prompt_type,
        'question': question.question,
        'media_file_url': media_file_url,
        'media_url': question.media_url,
        'answer_options': question.answer_options or [],
        'order': getattr(question, 'order', 0),
        'student_answer': student_answer,
        'requires_student_response': question.requires_student_response,
    }


def build_listening_sections(questions: list) -> list[dict]:
    """Group ordered quiz questions into IELTS-style audio sections."""
    sections: list[dict] = []
    current: dict | None = None
    question_number = 0

    for question in questions:
        prompt_type = (
            question.get('prompt_type')
            if isinstance(question, dict)
            else question.prompt_type
        )
        if prompt_type == 'audio':
            current = {'audio': question, 'questions': []}
            sections.append(current)
            continue

        requires_response = (
            question.get('requires_student_response')
            if isinstance(question, dict)
            else question.requires_student_response
        )
        if not requires_response:
            continue

        if current is None:
            current = {'audio': None, 'questions': []}
            sections.append(current)

        question_number += 1
        if isinstance(question, dict):
            question = {**question, 'number': question_number}
        current['questions'].append(question)

    return sections


def serialize_quiz_question(question):
    media_file_url = ''
    if question.media_file:
        try:
            media_file_url = question.media_file.url
        except ValueError:
            media_file_url = ''

    return {
        'id': question.pk,
        'quiz_id': question.quiz_id,
        'prompt_type': question.prompt_type,
        'question': question.question,
        'media_file_url': media_file_url,
        'media_url': question.media_url,
        'answer_options': question.answer_options or [],
        'correct_option_index': question.correct_option_index,
        'correct_option_letter': _quiz_correct_option_letter(question),
        'correct_answer': question.correct_answer,
        'order': question.order,
    }


def serialize_quiz_result(row):
    question_count = getattr(row, 'question_count', None)
    quiz = row.quiz
    if question_count is None:
        question_count = row.quiz.questions.count()
    return {
        'id': row.pk,
        'student_id': row.student_id,
        'student_name': row.student.full_name,
        'quiz_id': row.quiz_id,
        'quiz_topic': quiz.topic,
        'grading_mode': quiz.grading_mode,
        'grading_mode_label': quiz.get_grading_mode_label(),
        'is_manual_grading': quiz.is_manual_grading,
        'total_score': row.total_score,
        'max_value': quiz.score_max_value(question_count=question_count),
        'duration_sec': row.duration_sec,
        'student_submission': row.student_submission,
        'teacher_feedback': row.teacher_feedback,
        'reviewed_at': row.reviewed_at,
        'is_pending_review': row.is_pending_review,
        'completed_at': row.completed_at,
    }


def serialize_quiz_result_as_score(row):
    data = serialize_quiz_result(row)
    value = data['total_score']
    if data['is_pending_review']:
        value_label = None
    elif value is None:
        value_label = None
    else:
        value_label = value
    return {
        'id': f"quiz-{data['id']}",
        'result_id': data['id'],
        'source': 'quiz',
        'student_id': data['student_id'],
        'student_name': data['student_name'],
        'score_type': Score.ScoreType.QUIZ,
        'score_type_label': Score.ScoreType.QUIZ.label,
        'value': value_label,
        'max_value': data['max_value'],
        'date': data['completed_at'],
        'comment': data['teacher_feedback'],
        'lesson_id': None,
        'lesson_title': data['quiz_topic'],
        'quiz_topic': data['quiz_topic'],
        'is_pending_review': data['is_pending_review'],
        'is_manual_grading': data['is_manual_grading'],
        'grading_mode_label': data.get('grading_mode_label', ''),
    }


def _merge_student_scores(quiz_rows, admin_rows, limit=200):
    merged = []
    for row in quiz_rows:
        merged.append({**row, 'sort_date': row.get('date')})
    for row in admin_rows:
        merged.append({**row, 'sort_date': row.get('date')})
    merged.sort(key=lambda item: item.get('sort_date') or '', reverse=True)
    for row in merged:
        row.pop('sort_date', None)
    return merged[:limit]


def _quiz_results_queryset():
    return (
        QuizResult.objects.select_related('student', 'quiz')
        .annotate(question_count=Count('quiz__questions', distinct=True))
        .order_by('-completed_at', '-id')
    )


def resolve_scores_view_param(request, quiz_scores, weekly_scores, mock_attempts=None):
    """Pick active scores tab from query string or sensible default."""
    scores_view = request.GET.get('view')
    if scores_view == 'lesson':
        scores_view = 'weekly'
    valid_views = ('quiz', 'weekly')
    if mock_attempts is not None:
        valid_views = ('quiz', 'weekly', 'mock')
    if scores_view in valid_views:
        return scores_view
    if not quiz_scores and weekly_scores:
        return 'weekly'
    if not quiz_scores and not weekly_scores and mock_attempts:
        return 'mock'
    return 'quiz'


def split_student_quiz_results(rows):
    manual_quiz_results = [row for row in rows if row.get('is_manual_grading')]
    auto_quiz_results = [row for row in rows if not row.get('is_manual_grading')]
    return manual_quiz_results, auto_quiz_results


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_quizzes(teacher_id):
    from portals.utils.student_courses import quiz_visible_to_teacher

    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return []
    qs = (
        Quiz.objects.filter(
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related('questions')
        .distinct()
        .order_by('-created_at', 'id')
    )
    visible = [row for row in qs if quiz_visible_to_teacher(row, teacher_id)]
    return [serialize_quiz(row) for row in visible]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_quiz_detail(teacher_id, quiz_id):
    from portals.utils.student_courses import quiz_visible_to_teacher

    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return None
    quiz = (
        Quiz.objects.filter(
            pk=quiz_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related(
            Prefetch('questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
        )
        .first()
    )
    if not quiz or not quiz_visible_to_teacher(quiz, teacher_id):
        return None
    return {
        **serialize_quiz(quiz),
        'questions': [serialize_quiz_question(q) for q in quiz.questions.all()],
    }


def get_student_quiz_take_data(student_id, quiz_id):
    from portals.utils.student_courses import quiz_visible_to_student

    course_codes = get_student_course_type_codes(student_id)
    if not course_codes:
        return None
    quiz = (
        Quiz.objects.filter(
            pk=quiz_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related(
            Prefetch('questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
        )
        .first()
    )
    if not quiz or not quiz_visible_to_student(quiz, student_id):
        return None
    if not quiz.is_variant_quiz:
        return None

    questions = [q for q in quiz.questions.all() if q.is_answerable]
    if not questions:
        return None
    return {
        **serialize_quiz(quiz),
        'questions': [serialize_quiz_question_for_student(q) for q in questions],
    }


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_manual_quiz_take_data(student_id, quiz_id):
    from portals.utils.student_courses import quiz_visible_to_student
    from portals.utils.quiz_submit import build_essay_question_responses, student_can_take_manual_quiz

    course_codes = get_student_course_type_codes(student_id)
    if not course_codes:
        return None
    quiz = (
        Quiz.objects.filter(
            pk=quiz_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related(
            Prefetch('questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
        )
        .first()
    )
    if not quiz or not quiz_visible_to_student(quiz, student_id):
        return None
    if not quiz.is_manual_grading:
        return None
    questions = [q for q in quiz.questions.all() if q.is_answerable]
    if not questions:
        return None

    def serialize_questions(question_rows, response_map=None, single_submission=''):
        response_map = response_map or {}
        return [
            serialize_quiz_question_for_student(
                q,
                student_answer=response_map.get(
                    str(q.pk),
                    single_submission if len(question_rows) == 1 else '',
                ),
            )
            for q in question_rows
        ]

    listening_sections = []

    existing = (
        QuizResult.objects.filter(student_id=student_id, quiz_id=quiz_id)
        .select_related('quiz')
        .prefetch_related(
            Prefetch('quiz__questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
        )
        .first()
    )
    can_take = student_can_take_manual_quiz(student_id, quiz_id)
    if existing and existing.is_pending_review:
        response_map = {
            str(item['id']): item['student_answer']
            for item in build_essay_question_responses(existing)
        }
        single_submission = (existing.student_submission or '').strip()
        serialized = serialize_questions(questions, response_map, single_submission)
        if quiz.is_listening:
            listening_sections = build_listening_sections(serialized)
        response_ids = [q['id'] for q in serialized if q.get('requires_student_response')]
        return {
            **serialize_quiz(quiz),
            'questions': serialized,
            'listening_sections': listening_sections,
            'response_question_ids': response_ids,
            'response_question_count': len(response_ids),
            'view_only': True,
            'is_pending_review': True,
            'result_id': existing.pk,
        }
    if not can_take:
        return None
    serialized = serialize_questions(questions)
    if quiz.is_listening:
        listening_sections = build_listening_sections(serialized)
    response_ids = [q['id'] for q in serialized if q.get('requires_student_response')]
    return {
        **serialize_quiz(quiz),
        'questions': serialized,
        'listening_sections': listening_sections,
        'response_question_ids': response_ids,
        'response_question_count': len(response_ids),
        'view_only': False,
    }


def serialize_quiz_result_review(row):
    from portals.utils.quiz_submit import build_essay_question_responses

    quiz = row.quiz
    data = {
        **serialize_quiz_result(row),
        'student_submission': row.student_submission,
        'teacher_feedback': row.teacher_feedback,
        'grading_mode_label': quiz.get_grading_mode_label(),
        'is_essay': quiz.is_essay,
        'questions': [serialize_quiz_question(q) for q in quiz.questions.all()],
    }
    if quiz.is_essay or quiz.uses_per_question_text_responses:
        data['question_responses'] = build_essay_question_responses(row)
    return data


def _teacher_pending_quiz_results_queryset(teacher_id):
    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return None
    return (
        QuizResult.objects.filter(
            reviewed_at__isnull=True,
            quiz__category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
            student__groups__teacher_id=teacher_id,
            student__groups__courses__slug__in=expand_course_types_to_service_slugs(course_codes),
            student__groups__is_active=True,
        )
        .filter(
            Q(quiz__is_listening=True) | Q(quiz__is_essay=True) | Q(quiz__is_speaking=True),
        )
        .select_related('student', 'quiz', 'quiz__category')
        .distinct()
        .order_by('-completed_at', 'id')
    )


def get_teacher_pending_quiz_results(teacher_id):
    from portals.utils.student_courses import filter_quiz_results_for_teacher

    qs = _teacher_pending_quiz_results_queryset(teacher_id)
    if qs is None:
        return []
    qs = qs.prefetch_related(
        Prefetch('quiz__questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
    )
    visible = filter_quiz_results_for_teacher(qs, teacher_id)
    return [serialize_quiz_result_review(row) for row in visible[:100]]


def get_teacher_quiz_result_detail(teacher_id, result_id):
    from portals.utils.student_courses import teacher_can_see_quiz_result

    row = (
        QuizResult.objects.filter(pk=result_id)
        .select_related('student', 'quiz', 'quiz__category')
        .prefetch_related(
            Prefetch('quiz__questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
        )
        .first()
    )
    if not row or not row.quiz.is_manual_grading:
        return None
    if not teacher_can_see_quiz_result(teacher_id, row.student_id, row.quiz):
        return None
    return serialize_quiz_result_review(row)
def get_student_quizzes(student_id):
    from portals.models import Quiz
    from portals.utils.student_courses import filter_quizzes_for_student

    codes = get_student_course_type_codes(student_id)
    if not codes:
        return []
    qs = (
        Quiz.objects.filter(category__services__slug__in=quiz_category_slugs_for_portal_codes(codes))
        .select_related('category')
        .prefetch_related('questions')
        .distinct()
        .order_by('-created_at', 'id')
    )
    visible = filter_quizzes_for_student(qs, student_id)
    return [serialize_quiz(row) for row in visible]
def get_student_quiz_results(student_id):
    from portals.utils.student_courses import filter_quiz_results_for_student

    codes = get_student_course_type_codes(student_id)
    if not codes:
        return []
    qs = (
        _quiz_results_queryset()
        .filter(
            student_id=student_id,
            quiz__category__services__slug__in=quiz_category_slugs_for_portal_codes(codes),
        )
        .select_related('quiz__category')
        .distinct()
    )
    visible = filter_quiz_results_for_student(qs, student_id)
    return [serialize_quiz_result(row) for row in visible]
def get_parent_child_quiz_results(student_id, *, parent_id=None):
    from portals.utils.parent_access import parent_can_access_student

    if parent_id is not None and not parent_can_access_student(parent_id, student_id):
        return []
    return get_student_quiz_results(student_id)
def get_teacher_student_quiz_results(teacher_id, student_id):
    from portals.utils.student_courses import filter_quiz_results_for_teacher
    from portals.utils.teacher_access import get_teacher_student

    if not get_teacher_student(teacher_id, student_id):
        return []
    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return []
    qs = (
        _quiz_results_queryset()
        .filter(
            student_id=student_id,
            quiz__category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('quiz__category')
        .distinct()
    )
    visible = filter_quiz_results_for_teacher(qs, teacher_id)
    return [serialize_quiz_result(row) for row in visible]

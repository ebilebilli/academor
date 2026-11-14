"""Homework quizzes: quizzes a teacher attached to a lesson.

A lesson goes to a group or straight to students. Its quizzes are open for every
recipient: through the group for a group lesson, through the student for a direct one.
That access does not depend on the student's services or on per-quiz switches.
"""

from django.db.models import Q

from portals.models import Lesson
from portals.utils.cache_utils import cached_query


def student_lessons_q(student_id, prefix=''):
    """Q for Lesson rows (or a relation to them via ``prefix``) this student receives."""
    return (
        Q(**{f'{prefix}group__students__pk': student_id, f'{prefix}group__is_active': True})
        | Q(**{f'{prefix}students__pk': student_id})
    )


def student_lessons_qs(student_id):
    if not student_id:
        return Lesson.objects.none()
    return Lesson.objects.filter(student_lessons_q(student_id)).distinct()


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_homework_quiz_ids(student_id):
    """Ids of quizzes this student got as homework (sorted list, cache-friendly)."""
    if not student_id:
        return []
    return sorted(
        quiz_id
        for quiz_id in student_lessons_qs(student_id)
        .values_list('quizzes__pk', flat=True)
        .distinct()
        if quiz_id
    )


def quiz_is_homework_for_student(quiz_id, student_id):
    if not quiz_id or not student_id:
        return False
    return quiz_id in set(get_student_homework_quiz_ids(student_id))


def teacher_gave_quiz_as_homework(teacher_id, student_id, quiz_id):
    """True when this teacher attached the quiz to a lesson that reaches the student."""
    if not teacher_id or not student_id or not quiz_id:
        return False
    return (
        student_lessons_qs(student_id)
        .filter(teacher_id=teacher_id, quizzes__pk=quiz_id)
        .exists()
    )


def lesson_recipients_qs(lesson, *, include_inactive=False):
    """Students who receive a lesson: the group's students, or the chosen ones."""
    from portals.models import StudentProfile

    if lesson is None or not lesson.pk:
        return StudentProfile.objects.none()
    if lesson.group_id:
        qs = StudentProfile.objects.filter(groups__pk=lesson.group_id)
    else:
        qs = StudentProfile.objects.filter(direct_lessons__pk=lesson.pk)
    if not include_inactive:
        qs = qs.filter(is_active=True)
    return qs.distinct()


# ---------------------------------------------------------------- lesson page rows
def quiz_take_url_name(quiz):
    """Student take page for a quiz format (same routing as the quiz category page)."""
    if getattr(quiz, 'is_reading', False):
        return 'portals:student-reading-quiz-take'
    if getattr(quiz, 'is_speaking', False):
        return 'portals:student-speaking-quiz-take'
    if getattr(quiz, 'is_listening', False) or getattr(quiz, 'is_manual_grading', False):
        return 'portals:student-manual-quiz-take'
    return 'portals:student-quiz-take'


def _latest_results(quiz_ids, student_ids):
    """(student_id, quiz_id) -> latest QuizResult."""
    from portals.models import QuizResult

    latest = {}
    if not quiz_ids or not student_ids:
        return latest
    rows = (
        QuizResult.objects.filter(quiz_id__in=quiz_ids, student_id__in=student_ids)
        .order_by('student_id', 'quiz_id', '-completed_at', '-id')
        .select_related('quiz')
    )
    for row in rows:
        latest.setdefault((row.student_id, row.quiz_id), row)
    return latest


def _result_payload(result, quiz):
    if result is None:
        return None
    from portals.utils.notifications import is_quiz_result_published

    published = is_quiz_result_published(result)
    return {
        'id': result.pk,
        'completed_at': result.completed_at,
        'is_published': published,
        'is_pending_review': bool(quiz.is_manual_grading and not result.reviewed_at),
        'total_score': result.total_score if published else None,
    }


def student_lesson_quiz_rows(lesson, student_id):
    """Homework quizzes on a lesson, for the student: take link + their latest result."""
    from django.urls import reverse

    quizzes = list(lesson.quizzes.select_related('category').order_by('topic', 'id'))
    latest = _latest_results([quiz.pk for quiz in quizzes], [student_id])
    rows = []
    for quiz in quizzes:
        result = latest.get((student_id, quiz.pk))
        rows.append({
            'id': quiz.pk,
            'topic': quiz.topic,
            'category_name': quiz.category.name if quiz.category_id else '',
            'take_url': reverse(quiz_take_url_name(quiz), kwargs={'pk': quiz.pk}),
            'score_url': (
                reverse('portals:student-score-detail', kwargs={'result_pk': result.pk})
                if result is not None else ''
            ),
            'result': _result_payload(result, quiz),
        })
    return rows


def teacher_lesson_quiz_rows(lesson):
    """Homework quizzes on a lesson, for the teacher: every recipient's latest result."""
    from django.urls import reverse

    quizzes = list(lesson.quizzes.select_related('category').order_by('topic', 'id'))
    if not quizzes:
        return []
    students = list(
        lesson_recipients_qs(lesson).select_related('user').order_by('user__username', 'id')
    )
    latest = _latest_results([quiz.pk for quiz in quizzes], [student.pk for student in students])
    rows = []
    for quiz in quizzes:
        student_rows = []
        done = 0
        for student in students:
            result = latest.get((student.pk, quiz.pk))
            if result is not None:
                done += 1
            student_rows.append({
                'student_id': student.pk,
                'student_name': student.full_name,
                'profile_url': reverse(
                    'portals:teacher-student-profile',
                    kwargs={'student_pk': student.pk},
                ),
                'result_url': (
                    reverse('portals:teacher-score-detail', kwargs={'result_pk': result.pk})
                    if result is not None else ''
                ),
                'result': _result_payload(result, quiz),
            })
        rows.append({
            'id': quiz.pk,
            'topic': quiz.topic,
            'category_name': quiz.category.name if quiz.category_id else '',
            'done_count': done,
            'student_count': len(students),
            'students': student_rows,
        })
    return rows

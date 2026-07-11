"""Per-student quiz and mock-test access controlled by teachers."""

from django.db import transaction

from portals.models import Quiz, QuizAssignment, StudentMockAccess
from portals.utils.cache_utils import invalidate_model_cache
from portals.utils.mock_programs import MOCK_EXAM_PROGRAMS, get_program_label
from portals.utils.student_courses import (
    get_quiz_service_code,
    get_student_course_type_codes,
    quiz_visible_to_teacher,
    student_has_course_access,
)
from portals.utils.teacher_access import get_teacher_student

IELTS_SERVICE = 'ielts'


def student_has_active_quiz_assignment(student_id, quiz_id):
    if not student_id or not quiz_id:
        return False
    try:
        return QuizAssignment.objects.filter(
            student_id=student_id,
            quiz_id=quiz_id,
            is_active=True,
        ).exists()
    except Exception:
        # Table missing before migrate — fall back to enrollment-only access.
        return True


def get_student_quiz_assignment_map(student_id, quiz_ids):
    """quiz_id → is_active for the given ids (missing rows mean inactive)."""
    if not student_id or not quiz_ids:
        return {}
    try:
        return {
            row.quiz_id: row.is_active
            for row in QuizAssignment.objects.filter(
                student_id=student_id,
                quiz_id__in=list(quiz_ids),
            )
        }
    except Exception:
        return {quiz_id: True for quiz_id in quiz_ids}


def teacher_can_manage_student_quiz(teacher_id, student_id, quiz):
    if not get_teacher_student(teacher_id, student_id):
        return False
    if not quiz or not quiz_visible_to_teacher(quiz, teacher_id):
        return False
    service = get_quiz_service_code(quiz)
    return bool(service) and student_has_course_access(student_id, service)


def set_student_quiz_assignment(teacher_id, student_id, quiz_id, *, is_active):
    quiz = (
        Quiz.objects.filter(pk=quiz_id)
        .select_related('category')
        .first()
    )
    if not teacher_can_manage_student_quiz(teacher_id, student_id, quiz):
        return None

    with transaction.atomic():
        assignment, _created = QuizAssignment.objects.update_or_create(
            student_id=student_id,
            quiz_id=quiz_id,
            defaults={
                'is_active': bool(is_active),
                'assigned_by_id': teacher_id,
            },
        )
    invalidate_model_cache('QuizAssignment')
    return assignment


def student_has_active_mock_access_for_program(student_id, exam_program):
    if not student_id or not exam_program:
        return False
    if not student_has_course_access(student_id, exam_program):
        return False
    try:
        return StudentMockAccess.objects.filter(
            student_id=student_id,
            exam_program=exam_program,
            is_active=True,
        ).exists()
    except Exception:
        return True


def student_has_active_mock_access(student_id):
    from portals.utils.ielts_mock_test import get_student_mock_exam_programs

    programs = get_student_mock_exam_programs(student_id)
    if not programs:
        return False
    return any(
        student_has_active_mock_access_for_program(student_id, program)
        for program in programs
    )


def get_student_mock_access_state(student_id, exam_program):
    from portals.utils.ielts_mock_test import get_student_mock_exam_programs

    if exam_program not in get_student_mock_exam_programs(student_id):
        return None
    try:
        row = StudentMockAccess.objects.filter(
            student_id=student_id,
            exam_program=exam_program,
        ).first()
    except Exception:
        return {'is_active': True, 'exists': False}
    if not row:
        return {'is_active': False, 'exists': False}
    return {'is_active': bool(row.is_active), 'exists': True}


def get_teacher_manageable_mock_programs(teacher_id, student_id):
    from portals.models import TeacherCourseSpecialization
    from portals.utils.ielts_mock_test import get_student_mock_exam_programs

    if not get_teacher_student(teacher_id, student_id):
        return []
    student_programs = set(get_student_mock_exam_programs(student_id))
    teacher_programs = set(
        TeacherCourseSpecialization.objects.filter(teacher_id=teacher_id)
        .values_list('course_type', flat=True)
    )
    return sorted(student_programs & teacher_programs & set(MOCK_EXAM_PROGRAMS))


def get_teacher_student_mock_access_rows(teacher_id, student_id):
    rows = []
    for program in get_teacher_manageable_mock_programs(teacher_id, student_id):
        state = get_student_mock_access_state(student_id, program) or {
            'is_active': False,
            'exists': False,
        }
        rows.append({
            'program': program,
            'label': get_program_label(program),
            'is_active': state['is_active'],
            'exists': state['exists'],
        })
    return rows


def set_student_mock_access(teacher_id, student_id, exam_program, *, is_active):
    from portals.utils.ielts_mock_test import get_student_mock_exam_programs

    if exam_program not in MOCK_EXAM_PROGRAMS:
        return None
    if exam_program not in get_teacher_manageable_mock_programs(teacher_id, student_id):
        return None
    if exam_program not in get_student_mock_exam_programs(student_id):
        return None

    with transaction.atomic():
        access, _created = StudentMockAccess.objects.update_or_create(
            student_id=student_id,
            exam_program=exam_program,
            defaults={
                'is_active': bool(is_active),
                'assigned_by_id': teacher_id,
            },
        )
    invalidate_model_cache('StudentMockAccess')
    invalidate_model_cache('QuizAssignment')
    return access


def _quiz_format_label(quiz):
    if quiz.is_reading:
        return 'Reading'
    if quiz.is_listening:
        return 'Listening'
    if quiz.is_speaking:
        return 'Speaking'
    if quiz.is_essay:
        return 'Writing'
    return 'Variant'


def get_teacher_student_quiz_access_rows(teacher_id, student_id):
    """Quizzes the teacher may assign, grouped by category, with active state."""
    if not get_teacher_student(teacher_id, student_id):
        return []

    student_codes = set(get_student_course_type_codes(student_id))
    if not student_codes:
        return []

    quizzes = (
        Quiz.objects.filter(category__service__in=student_codes)
        .select_related('category')
        .order_by('category__service', 'category__name', '-created_at', 'id')
    )
    visible_quizzes = [row for row in quizzes if quiz_visible_to_teacher(row, teacher_id)]
    if not visible_quizzes:
        return []

    assignment_map = get_student_quiz_assignment_map(
        student_id,
        [quiz.pk for quiz in visible_quizzes],
    )

    categories = []
    category_index = {}
    for quiz in visible_quizzes:
        category = quiz.category
        bucket = category_index.get(category.pk)
        if bucket is None:
            from portals.utils.portal_services import resolve_course_type_label

            bucket = {
                'id': category.pk,
                'name': category.name,
                'service': category.service,
                'service_label': resolve_course_type_label(category.service),
                'quizzes': [],
            }
            category_index[category.pk] = bucket
            categories.append(bucket)
        bucket['quizzes'].append({
            'id': quiz.pk,
            'topic': quiz.topic,
            'format_label': _quiz_format_label(quiz),
            'is_active': assignment_map.get(quiz.pk, False),
        })
    return categories

"""Student course / service access via the student's own enrollments.

Access never comes from a group: a group is only a name. A student sees a quiz when
they are enrolled in its service (plus the per-quiz switch for IELTS/SAT), or when a
teacher gave it to them as homework on a lesson.
"""

from portals.models import StudentCourseSpecialization
from portals.utils.cache_utils import cached_query
from portals.utils.portal_services import portal_course_keys_overlap

IELTS_COURSE_CODE = 'ielts'
GENERAL_ENGLISH_COURSE_CODE = 'general_english'

SCORE_LIST_LIMIT = 200
QUIZ_HISTORY_INITIAL_SIZE = 10
QUIZ_HISTORY_PAGE_SIZE = 10


def _course_type_keys(code):
    """Every stored key (the code + its service slugs) that means this portal code."""
    from portals.utils.portal_services import expand_course_types_to_service_slugs

    return set(expand_course_types_to_service_slugs([code])) | {code}


def student_course_enrollment(student_id, code):
    """The student's enrollment row for a portal code (stored as the code or a slug), or None."""
    if not student_id or not code:
        return None
    return (
        StudentCourseSpecialization.objects.filter(
            student_id=student_id,
            course_type__in=_course_type_keys(code),
        )
        .order_by('-is_active', 'id')
        .first()
    )


def set_student_course_enrollment(student_id, code, *, is_active):
    """Switch one service on or off for a student. Returns the row, or None if the code is unknown."""
    from portals.utils.portal_services import is_active_portal_course_type, normalize_portal_course_type

    if not student_id or not code:
        return None
    rows = StudentCourseSpecialization.objects.filter(
        student_id=student_id,
        course_type__in=_course_type_keys(code),
    )
    if rows.exists():
        rows.exclude(is_active=bool(is_active)).update(is_active=bool(is_active))
        row = rows.order_by('id').first()
    else:
        course_type = normalize_portal_course_type(code) or code
        if not is_active_portal_course_type(course_type):
            return None
        row = StudentCourseSpecialization.objects.create(
            student_id=student_id,
            course_type=course_type,
            is_active=bool(is_active),
        )
    from portals.utils.cache_utils import invalidate_model_cache

    invalidate_model_cache('StudentCourseSpecialization')
    return row


def set_student_services(student_id, codes):
    """Give a student exactly these services (others are switched off, never deleted)."""
    wanted = {code for code in (codes or []) if code}
    keep_keys = set()
    for code in wanted:
        keep_keys |= _course_type_keys(code)
        set_student_course_enrollment(student_id, code, is_active=True)
    StudentCourseSpecialization.objects.filter(student_id=student_id, is_active=True).exclude(
        course_type__in=keep_keys,
    ).update(is_active=False)
    from portals.utils.cache_utils import invalidate_model_cache

    invalidate_model_cache('StudentCourseSpecialization')


def ensure_general_english_for_ielts(student_id):
    """IELTS students get General English on by default (only when they have no row for it yet)."""
    from portals.utils.portal_services import is_active_portal_course_type

    if not student_id or not is_active_portal_course_type(GENERAL_ENGLISH_COURSE_CODE):
        return None
    if student_course_enrollment(student_id, GENERAL_ENGLISH_COURSE_CODE) is not None:
        return None  # a teacher may have switched it off on purpose
    return set_student_course_enrollment(student_id, GENERAL_ENGLISH_COURSE_CODE, is_active=True)


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_course_type_codes(student_id):
    """Active service enrollments assigned directly on the student profile.

    Cached: quiz/classroom visibility checks call this once per row in list
    loops, which was an N+1 hotspot.
    """
    if not student_id:
        return []
    return sorted(
        StudentCourseSpecialization.objects.filter(
            student_id=student_id,
            is_active=True,
        )
        .values_list('course_type', flat=True)
        .distinct()
    )


def student_has_course_access(student_id, course_type):
    if not student_id or not course_type:
        return False
    return course_type in get_student_course_type_codes(student_id)


def get_quiz_service_code(quiz):
    if not quiz or not getattr(quiz, 'category_id', None):
        return ''
    from portals.utils.quiz_category_services import quiz_category_primary_portal_code

    category = getattr(quiz, 'category', None)
    if category is not None:
        return quiz_category_primary_portal_code(category)
    return ''


def get_quiz_portal_course_codes(quiz):
    if not quiz or not getattr(quiz, 'category_id', None):
        return []
    from portals.utils.quiz_category_services import quiz_category_portal_codes

    category = getattr(quiz, 'category', None)
    if category is not None:
        return quiz_category_portal_codes(category)
    return []


def student_quiz_enrollment_ok(student_id, quiz):
    """True when the student is enrolled in the quiz service (ignores assignment)."""
    codes = get_quiz_portal_course_codes(quiz)
    if not codes:
        return False
    return portal_course_keys_overlap(codes, get_student_course_type_codes(student_id))


def quiz_is_student_homework(quiz, student_id):
    from portals.utils.lesson_quizzes import quiz_is_homework_for_student

    return bool(quiz) and quiz_is_homework_for_student(quiz.pk, student_id)


def student_can_reach_quiz(student_id, quiz):
    """Enrolled in the quiz service, or got the quiz as homework (ignores per-quiz switches)."""
    return student_quiz_enrollment_ok(student_id, quiz) or quiz_is_student_homework(quiz, student_id)


def quiz_visible_to_student(quiz, student_id):
    # A quiz given as homework is open for that student, whatever their services.
    if quiz_is_student_homework(quiz, student_id):
        return True
    if not student_quiz_enrollment_ok(student_id, quiz):
        return False
    from portals.utils.quiz_assignments import (
        quiz_has_program_flag,
        student_has_active_quiz_assignment,
    )

    # Regular (non-IELTS/SAT) quizzes stay open once the student is enrolled.
    if not quiz_has_program_flag(quiz):
        return True
    return student_has_active_quiz_assignment(student_id, quiz.pk)


def quiz_visible_to_teacher(quiz, teacher_id):
    from portals.utils.teacher_courses import get_teacher_course_type_codes

    codes = get_quiz_portal_course_codes(quiz)
    if not codes:
        return False
    return portal_course_keys_overlap(codes, get_teacher_course_type_codes(teacher_id))


def filter_quizzes_for_student(quizzes, student_id):
    from portals.utils.quiz_assignments import (
        get_student_quiz_assignment_map,
        quiz_has_program_flag,
    )

    from portals.utils.lesson_quizzes import get_student_homework_quiz_ids

    homework_ids = set(get_student_homework_quiz_ids(student_id))
    enrolled = [
        quiz
        for quiz in quizzes
        if quiz.pk in homework_ids or student_quiz_enrollment_ok(student_id, quiz)
    ]
    flagged = [
        quiz for quiz in enrolled
        if quiz.pk not in homework_ids and quiz_has_program_flag(quiz)
    ]
    if not flagged:
        return enrolled
    # Same rule as quiz_visible_to_student, resolved in one query instead of an
    # exists() per IELTS/SAT quiz. A missing row means inactive in both paths.
    assignment_map = get_student_quiz_assignment_map(
        student_id,
        [quiz.pk for quiz in flagged],
    )
    return [
        quiz
        for quiz in enrolled
        if quiz.pk in homework_ids
        or not quiz_has_program_flag(quiz)
        or assignment_map.get(quiz.pk, False)
    ]


def filter_quiz_results_for_student(results, student_id):
    visible = []
    for row in results:
        quiz = getattr(row, 'quiz', None)
        # Past results stay visible even if the teacher later locks the quiz.
        if quiz and student_can_reach_quiz(student_id, quiz):
            visible.append(row)
    return visible


def filter_quiz_results_for_teacher(results, teacher_id):
    """Results a teacher may see: the quiz is in their services and the student is theirs.

    The student must be enrolled in the quiz service, or have got the quiz as homework
    from this teacher. No per-row group queries.
    """
    from portals.models import CustomerProfile, Lesson
    from portals.utils.teacher_courses import get_teacher_course_type_codes
    from portals.utils.teacher_students import teacher_student_ids

    rows = list(results)
    if not rows or not teacher_id:
        return []

    teacher_codes = get_teacher_course_type_codes(teacher_id)
    if not teacher_codes:
        return []

    student_ids = {row.student_id for row in rows if row.student_id}
    customer_ids = {row.customer_id for row in rows if row.customer_id}
    own_students = teacher_student_ids(teacher_id) & student_ids if student_ids else set()
    homework_pairs = set()
    if own_students:
        # (student, quiz) pairs this teacher gave as homework: group lessons + direct lessons
        group_pairs = Lesson.objects.filter(
            teacher_id=teacher_id,
            group__isnull=False,
            group__is_active=True,
            group__students__pk__in=own_students,
            quizzes__isnull=False,
        ).values_list('group__students__pk', 'quizzes__pk')
        direct_pairs = Lesson.objects.filter(
            teacher_id=teacher_id,
            group__isnull=True,
            students__pk__in=own_students,
            quizzes__isnull=False,
        ).values_list('students__pk', 'quizzes__pk')
        for student_id, quiz_id in list(group_pairs) + list(direct_pairs):
            if student_id in own_students and quiz_id:
                homework_pairs.add((student_id, quiz_id))
    customer_teacher = {}
    if customer_ids:
        customer_teacher = dict(
            CustomerProfile.objects.filter(pk__in=customer_ids).values_list('pk', 'teacher_id')
        )

    student_codes_cache = {}
    visible = []
    for row in rows:
        quiz = getattr(row, 'quiz', None)
        if not quiz:
            continue
        quiz_codes = get_quiz_portal_course_codes(quiz)
        if not quiz_codes or not portal_course_keys_overlap(quiz_codes, teacher_codes):
            continue

        if row.customer_id:
            if customer_teacher.get(row.customer_id) != teacher_id:
                continue
            service = get_quiz_service_code(quiz)
            if service and portal_course_keys_overlap([service], teacher_codes):
                visible.append(row)
            continue

        sid = row.student_id
        if not sid or sid not in own_students:
            continue
        if (sid, quiz.pk) in homework_pairs:
            visible.append(row)
            continue
        if sid not in student_codes_cache:
            student_codes_cache[sid] = get_student_course_type_codes(sid)
        if portal_course_keys_overlap(quiz_codes, student_codes_cache[sid]):
            visible.append(row)
    return visible


def teacher_can_see_customer_quiz_result(teacher_id, customer_id, quiz):
    """Assigned teacher sees customer mock manual-review results for their IELTS courses."""
    from portals.models import CustomerProfile
    from portals.utils.teacher_courses import get_teacher_course_type_codes

    if not quiz or not customer_id or not teacher_id:
        return False
    if not quiz_visible_to_teacher(quiz, teacher_id):
        return False
    customer_teacher_id = (
        CustomerProfile.objects.filter(pk=customer_id)
        .values_list('teacher_id', flat=True)
        .first()
    )
    if customer_teacher_id != teacher_id:
        return False
    service = get_quiz_service_code(quiz)
    if not service:
        return False
    return portal_course_keys_overlap([service], get_teacher_course_type_codes(teacher_id))


def teacher_can_review_quiz_result(teacher_id, result) -> bool:
    quiz = getattr(result, 'quiz', None)
    if getattr(result, 'customer_id', None):
        return teacher_can_see_customer_quiz_result(teacher_id, result.customer_id, quiz)
    return teacher_can_see_quiz_result(teacher_id, result.student_id, quiz)


def teacher_can_see_quiz_result(teacher_id, student_id, quiz):
    """Teacher sees a result when the student is theirs and the quiz is in their services.

    The student is enrolled in the quiz service, or got the quiz as homework from this
    teacher. Groups play no part: a student may have none.
    """
    from portals.utils.lesson_quizzes import teacher_gave_quiz_as_homework
    from portals.utils.teacher_students import teacher_has_student

    if not quiz or not quiz_visible_to_teacher(quiz, teacher_id):
        return False
    if not teacher_has_student(teacher_id, student_id):
        return False
    if student_quiz_enrollment_ok(student_id, quiz):
        return True
    return teacher_gave_quiz_as_homework(teacher_id, student_id, quiz.pk)


def _classroom_portal_codes(classroom):
    from portals.utils.portal_services import classroom_service_portal_codes

    if not classroom:
        return set()
    return set(classroom_service_portal_codes(classroom.services.all()))


def classroom_visible_to_student(classroom, student_id, *, student_group_ids=None):
    if getattr(classroom, 'group_id', None):
        if student_group_ids is not None:
            # Caller already knows the student's groups — skip the per-row
            # EXISTS query (N+1 in classroom list loops).
            return classroom.group_id in student_group_ids
        return classroom.group.students.filter(pk=student_id).exists()
    services = _classroom_portal_codes(classroom)
    if not services:
        return False
    return bool(services & set(get_student_course_type_codes(student_id)))


def classroom_visible_to_teacher(classroom, teacher_id):
    if getattr(classroom, 'group_id', None):
        return classroom.group.teacher_id == teacher_id
    from portals.utils.teacher_courses import get_teacher_course_type_codes

    services = _classroom_portal_codes(classroom)
    if not services:
        return False
    return bool(services & set(get_teacher_course_type_codes(teacher_id)))


def get_parent_course_type_codes(parent_id):
    from portals.models import ParentProfile

    if not parent_id:
        return []
    student_ids = (
        ParentProfile.objects.filter(pk=parent_id)
        .values_list('students__pk', flat=True)
        .distinct()
    )
    codes = set()
    for student_id in student_ids:
        if student_id:
            codes.update(get_student_course_type_codes(student_id))
    return sorted(codes)


def classroom_visible_to_parent(classroom, parent_id):
    if getattr(classroom, 'group_id', None):
        from portals.models import ParentProfile

        return ParentProfile.objects.filter(
            pk=parent_id,
            students__groups__pk=classroom.group_id,
        ).exists()
    services = _classroom_portal_codes(classroom)
    if not services:
        return False
    return bool(services & set(get_parent_course_type_codes(parent_id)))

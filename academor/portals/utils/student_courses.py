"""Student course / service access via direct enrollments on the student profile."""

from portals.models import StudentCourseSpecialization, StudyGroup
from portals.utils.cache_utils import cached_query
from portals.utils.portal_services import expand_course_types_to_service_slugs, portal_course_keys_overlap
from portals.utils.teacher_courses import teacher_groups_queryset

SCORE_LIST_LIMIT = 200
QUIZ_HISTORY_INITIAL_SIZE = 10
QUIZ_HISTORY_PAGE_SIZE = 10


def ensure_student_group_course_enrollments(student_id: int, group) -> None:
    """Ensure active StudentCourseSpecialization rows for the group's portal services.

    Not cached — this is a write helper invoked from M2M signals.
    """
    from portals.models import StudentCourseSpecialization
    from portals.utils.group_services import study_group_portal_codes
    from portals.utils.portal_services import is_active_portal_course_type, normalize_portal_course_type

    if not student_id or not group:
        return
    for code in study_group_portal_codes(group):
        course_type = normalize_portal_course_type(code)
        if not course_type or not is_active_portal_course_type(course_type):
            continue
        StudentCourseSpecialization.objects.update_or_create(
            student_id=student_id,
            course_type=course_type,
            defaults={'is_active': True},
        )


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
    return StudentCourseSpecialization.objects.filter(
        student_id=student_id,
        is_active=True,
        course_type=course_type,
    ).exists()


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


def quiz_visible_to_student(quiz, student_id):
    if not student_quiz_enrollment_ok(student_id, quiz):
        return False
    from portals.utils.quiz_assignments import student_has_active_quiz_assignment

    return student_has_active_quiz_assignment(student_id, quiz.pk)


def quiz_visible_to_teacher(quiz, teacher_id):
    from portals.utils.teacher_courses import get_teacher_course_type_codes

    codes = get_quiz_portal_course_codes(quiz)
    if not codes:
        return False
    return portal_course_keys_overlap(codes, get_teacher_course_type_codes(teacher_id))


def filter_quizzes_for_student(quizzes, student_id):
    return [quiz for quiz in quizzes if quiz_visible_to_student(quiz, student_id)]


def filter_quiz_results_for_student(results, student_id):
    visible = []
    for row in results:
        quiz = getattr(row, 'quiz', None)
        # Past results stay visible even if the teacher later locks the quiz.
        if quiz and student_quiz_enrollment_ok(student_id, quiz):
            visible.append(row)
    return visible


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_student_service_pairs(teacher_id):
    """Set of (student_id, service_slug) for active teacher groups — avoids N+1 per quiz row."""
    pairs = set()
    groups = teacher_groups_queryset(teacher_id, active_only=True).prefetch_related(
        'students',
        'courses',
    )
    for group in groups:
        slugs = {course.slug for course in group.courses.all() if course.slug}
        if not slugs:
            continue
        for student in group.students.all():
            for slug in slugs:
                pairs.add((student.pk, slug))
    return frozenset(pairs)


def filter_quiz_results_for_teacher(results, teacher_id):
    visible = []

    for row in results:
        quiz = getattr(row, 'quiz', None)
        if getattr(row, 'customer_id', None):
            if teacher_can_see_customer_quiz_result(teacher_id, row.customer_id, quiz):
                visible.append(row)
            continue

        if quiz and row.student_id and teacher_can_see_quiz_result(teacher_id, row.student_id, quiz):
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
    """Teacher sees a result when they teach the student and the quiz is in their services.

    Prefer a group whose courses overlap the quiz category. If the group's courses
    M2M is empty/misconfigured, fall back to any active shared group — parents do
    not need group courses, so this keeps teacher visibility aligned with that.
    """
    if not quiz or not quiz_visible_to_teacher(quiz, teacher_id):
        return False
    if not student_quiz_enrollment_ok(student_id, quiz):
        return False
    course_codes = get_quiz_portal_course_codes(quiz)
    if not course_codes:
        return False
    slugs = expand_course_types_to_service_slugs(course_codes)
    if not slugs:
        return False
    shared = StudyGroup.objects.filter(
        teacher_id=teacher_id,
        students__pk=student_id,
        is_active=True,
    )
    if shared.filter(courses__slug__in=slugs).exists():
        return True
    return shared.exists()


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

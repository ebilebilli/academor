"""Student course / service access via direct enrollments on the student profile."""

from portals.models import StudentCourseSpecialization, StudyGroup
from portals.utils.cache_utils import cached_query
from portals.utils.portal_services import expand_course_types_to_service_slugs
from portals.utils.teacher_courses import teacher_groups_queryset

SCORE_LIST_LIMIT = 200
QUIZ_HISTORY_INITIAL_SIZE = 10
QUIZ_HISTORY_PAGE_SIZE = 10


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
    return StudentCourseSpecialization.objects.filter(
        student_id=student_id,
        is_active=True,
        course_type=course_type,
    ).exists()


def get_quiz_service_code(quiz):
    if not quiz or not getattr(quiz, 'category_id', None):
        return ''
    category = getattr(quiz, 'category', None)
    if category is not None:
        return category.service or ''
    return ''


def quiz_visible_to_student(quiz, student_id):
    service = get_quiz_service_code(quiz)
    if not service:
        return False
    return service in set(get_student_course_type_codes(student_id))


def quiz_visible_to_teacher(quiz, teacher_id):
    from portals.utils.teacher_courses import get_teacher_course_type_codes

    service = get_quiz_service_code(quiz)
    if not service:
        return False
    return service in set(get_teacher_course_type_codes(teacher_id))


def filter_quizzes_for_student(quizzes, student_id):
    return [quiz for quiz in quizzes if quiz_visible_to_student(quiz, student_id)]


def filter_quiz_results_for_student(results, student_id):
    visible = []
    for row in results:
        quiz = getattr(row, 'quiz', None)
        if quiz and quiz_visible_to_student(quiz, student_id):
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
    from portals.utils.teacher_courses import get_teacher_course_type_codes

    teacher_codes = set(get_teacher_course_type_codes(teacher_id))
    if not teacher_codes:
        return []

    pairs = get_teacher_student_service_pairs(teacher_id)
    student_codes_cache = {}
    visible = []

    for row in results:
        quiz = getattr(row, 'quiz', None)
        if not quiz or not quiz_visible_to_teacher(quiz, teacher_id):
            continue

        service = get_quiz_service_code(quiz)
        if not service or service not in teacher_codes:
            continue

        student_id = row.student_id
        if student_id not in student_codes_cache:
            student_codes_cache[student_id] = set(get_student_course_type_codes(student_id))
        if service not in student_codes_cache[student_id]:
            continue

        if (student_id, service) in pairs:
            visible.append(row)
            continue

        expanded = expand_course_types_to_service_slugs([service])
        if any((student_id, slug) in pairs for slug in expanded):
            visible.append(row)

    return visible


def teacher_can_see_quiz_result(teacher_id, student_id, quiz):
    """Teacher sees a result for their student when group service matches the quiz category."""
    if not quiz or not quiz_visible_to_teacher(quiz, teacher_id):
        return False
    if not quiz_visible_to_student(quiz, student_id):
        return False
    service = get_quiz_service_code(quiz)
    if not service:
        return False
    slugs = expand_course_types_to_service_slugs([service])
    if not slugs:
        return False
    return StudyGroup.objects.filter(
        teacher_id=teacher_id,
        students__pk=student_id,
        is_active=True,
        courses__slug__in=slugs,
    ).exists()


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

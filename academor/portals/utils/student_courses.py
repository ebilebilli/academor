"""Student course / service access via direct enrollments on the student profile."""

from portals.models import StudentCourseSpecialization, StudyGroup
from portals.utils.portal_services import expand_course_types_to_service_slugs


def get_student_course_type_codes(student_id):
    """Active service enrollments assigned directly on the student profile."""
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


def filter_quiz_results_for_teacher(results, teacher_id):
    visible = []
    for row in results:
        quiz = getattr(row, 'quiz', None)
        if quiz and teacher_can_see_quiz_result(teacher_id, row.student_id, quiz):
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


def classroom_visible_to_student(classroom, student_id):
    services = _classroom_portal_codes(classroom)
    if not services:
        return False
    return bool(services & set(get_student_course_type_codes(student_id)))


def classroom_visible_to_teacher(classroom, teacher_id):
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
    services = _classroom_portal_codes(classroom)
    if not services:
        return False
    return bool(services & set(get_parent_course_type_codes(parent_id)))

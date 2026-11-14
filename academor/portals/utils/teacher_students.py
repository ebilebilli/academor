"""Who is whose student.

A student belongs to a teacher through any active group of that teacher, or directly
(``StudentProfile.teachers``) when the student has no group. Every "this teacher's
students" list and ownership check goes through here.
"""

from django.db.models import Q

from portals.models import StudentProfile, StudyGroup, TeacherProfile


def teacher_students_q(teacher_id, prefix=''):
    """Q for StudentProfile rows (or a relation to them via ``prefix``) of this teacher."""
    return (
        Q(**{f'{prefix}groups__teacher_id': teacher_id, f'{prefix}groups__is_active': True})
        | Q(**{f'{prefix}teachers__pk': teacher_id})
    )


def teacher_students_qs(teacher_id, *, include_inactive=False):
    if not teacher_id:
        return StudentProfile.objects.none()
    qs = StudentProfile.objects.filter(teacher_students_q(teacher_id)).distinct()
    if not include_inactive:
        qs = qs.filter(is_active=True)
    return qs


def teacher_student_ids(teacher_id, *, include_inactive=False):
    return set(
        teacher_students_qs(teacher_id, include_inactive=include_inactive)
        .values_list('pk', flat=True)
    )


def teacher_has_student(teacher_id, student_id, *, include_inactive=False):
    if not teacher_id or not student_id:
        return False
    return teacher_students_qs(teacher_id, include_inactive=include_inactive).filter(
        pk=student_id,
    ).exists()


def student_teacher_ids(student_id):
    """Teachers of a student: owners of their active groups plus direct teachers."""
    if not student_id:
        return set()
    ids = set(
        StudyGroup.objects.filter(students__pk=student_id, is_active=True)
        .values_list('teacher_id', flat=True)
    )
    ids.update(
        TeacherProfile.objects.filter(direct_students__pk=student_id).values_list('pk', flat=True)
    )
    ids.discard(None)
    return ids


def active_group_students(group):
    """A group's students without the deactivated ones (portal lists)."""
    return group.students.filter(is_active=True)


def default_services_for_teacher(teacher_id):
    """Services a new student gets when the teacher does not pick: theirs, else IELTS + General English."""
    from portals.teacher_forms import student_service_choices
    from portals.utils.portal_services import normalize_portal_course_type
    from portals.utils.student_courses import GENERAL_ENGLISH_COURSE_CODE, IELTS_COURSE_CODE
    from portals.utils.teacher_courses import get_teacher_course_type_codes

    valid = {code for code, _label in student_service_choices()}
    codes = {
        normalize_portal_course_type(code) or code
        for code in get_teacher_course_type_codes(teacher_id)
    } & valid
    if not codes:
        codes = {IELTS_COURSE_CODE, GENERAL_ENGLISH_COURSE_CODE} & valid
    if IELTS_COURSE_CODE in codes and GENERAL_ENGLISH_COURSE_CODE in valid:
        codes.add(GENERAL_ENGLISH_COURSE_CODE)
    return sorted(codes)


def create_teacher_student(teacher_id, name, *, services=None, group=None, phone='', password=''):
    """A real portal student made by a teacher: user + profile + teacher link + group + services.

    ``services`` None means the teacher's defaults. General English, switched on
    automatically for IELTS students, stays off when the teacher left it out on purpose.
    """
    from django.contrib.auth import get_user_model
    from django.db import transaction

    from portals.utils.student_courses import (
        GENERAL_ENGLISH_COURSE_CODE,
        set_student_course_enrollment,
        student_course_enrollment,
    )

    explicit = services is not None
    codes = list(services) if explicit else default_services_for_teacher(teacher_id)
    with transaction.atomic():
        user = get_user_model()(username=name, is_staff=False, is_superuser=False)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # cannot sign in until a password is set
        user.save()
        # no start date: the teacher may still mark earlier days of the month on the register
        student = StudentProfile.objects.create(
            user=user,
            phone=phone or '',
        )
        student.teachers.add(teacher_id)
        if group is not None:
            group.students.add(student)
        for code in codes:
            set_student_course_enrollment(student.pk, code, is_active=True)
        if (
            explicit
            and GENERAL_ENGLISH_COURSE_CODE not in codes
            and student_course_enrollment(student.pk, GENERAL_ENGLISH_COURSE_CODE) is not None
        ):
            set_student_course_enrollment(student.pk, GENERAL_ENGLISH_COURSE_CODE, is_active=False)
    return student

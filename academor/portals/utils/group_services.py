"""Study groups carry no services any more.

A group used to hand its linked site courses to its students (quiz, mock-test and
notification access) and to its lessons (the lesson's service). That is gone: a group
is only a name used for filtering, and access comes from each student's own services
(``StudentCourseSpecialization``). The helpers below stay so older call sites keep
working; the group-derived ones now answer "nothing".
"""

from django.db.models import Q


def study_group_portal_codes(group):
    """Groups have no services: always empty."""
    del group
    return []


def study_group_teaching_portal_codes(group):
    """Groups have no services: always empty."""
    del group
    return []


def study_group_portal_display_labels(group, lang=None):
    """Groups have no services: nothing to label."""
    del group, lang
    return []


def teacher_lesson_service_choices(teacher_id, lang=None):
    """Services a teacher may file a lesson under: their own specializations."""
    from portals.utils.teacher_courses import course_type_choices_for_teacher

    return list(course_type_choices_for_teacher(teacher_id, lang))


def resolve_teacher_default_lesson_service(teacher_id):
    """Service code a lesson gets when the teacher did not pick one."""
    from portals.utils.portal_services import DEFAULT_PORTAL_SERVICE_CODE

    choices = teacher_lesson_service_choices(teacher_id)
    return choices[0][0] if choices else DEFAULT_PORTAL_SERVICE_CODE


def resolve_group_lesson_service(group):
    """Legacy: the service of a lesson came from its group. Now from the group's teacher."""
    from portals.utils.portal_services import DEFAULT_PORTAL_SERVICE_CODE

    teacher_id = getattr(group, 'teacher_id', None)
    if not teacher_id:
        return DEFAULT_PORTAL_SERVICE_CODE
    return resolve_teacher_default_lesson_service(teacher_id)


def lesson_effective_subject(lesson):
    """Portal course code used for lesson lists, filters and labels: the one stored on the lesson."""
    from portals.utils.portal_services import normalize_portal_course_type

    return normalize_portal_course_type(lesson.subject) or (lesson.subject or '')


def study_group_courses_filter_q(codes, prefix=''):
    """Legacy: groups cannot be filtered by service any more (matches nothing)."""
    del codes, prefix
    return Q(pk__in=[])


def group_has_portal_code(group, code):
    del group, code
    return False


def students_matching_group_courses(group):
    """Students that may be put in a group: any active student (a group is only a name)."""
    from portals.models import StudentProfile

    qs = StudentProfile.objects.filter(is_active=True)
    if group is not None and getattr(group, 'pk', None):
        # keep current members selectable even after they were deactivated
        qs = StudentProfile.objects.filter(Q(is_active=True) | Q(groups__pk=group.pk)).distinct()
    return qs.select_related('user').order_by('user__username', 'id')


# Backward-compatible aliases.
study_group_services_filter_q = study_group_courses_filter_q

"""Teacher course specialization helpers (admin-assigned course access)."""

from django.utils.translation import get_language

from portals.models import StudyGroup, TeacherCourseSpecialization
from portals.utils.portal_services import (
    expand_course_types_to_service_slugs,
    get_active_course_type_choices,
    is_active_portal_course_type,
    resolve_course_type_label,
)


def get_teacher_course_type_codes(teacher_id):
    if not teacher_id:
        return []
    return list(
        TeacherCourseSpecialization.objects.filter(teacher_id=teacher_id)
        .values_list('course_type', flat=True)
        .order_by('course_type')
    )


def course_type_choices_for_teacher(teacher_id, lang=None):
    """Assigned specializations intersected with course types from active site services."""
    lang = lang or get_language()
    assigned = set(get_teacher_course_type_codes(teacher_id))
    if not assigned:
        return []

    active_choices = dict(get_active_course_type_choices(lang))
    result = []
    for code in sorted(assigned):
        if code in active_choices:
            result.append((code, active_choices[code]))
        else:
            # Legacy assignment when the service is inactive/unmapped — keep label for edits.
            result.append((code, resolve_course_type_label(code, lang)))
    return result


def teacher_has_course_access(teacher_id, course_type):
    if not teacher_id or not course_type:
        return False
    return TeacherCourseSpecialization.objects.filter(
        teacher_id=teacher_id,
        course_type=course_type,
    ).exists()


def teacher_groups_queryset(teacher_id, *, active_only=True):
    """Groups owned by the teacher (course access is derived from each group)."""
    qs = StudyGroup.objects.filter(teacher_id=teacher_id)
    if active_only:
        qs = qs.filter(is_active=True)
    return qs


def resolve_teacher_lesson_service(teacher_id, groups):
    """
    Pick course/service code for a lesson from selected groups.

    Legacy helper — prefers a single code shared by all groups; otherwise None.
    Portal lesson forms resolve service per group via resolve_group_lesson_service().
    """
    del teacher_id  # kept for backward-compatible call sites
    if not groups:
        return None
    from portals.utils.group_services import resolve_group_lesson_service

    codes = {resolve_group_lesson_service(group) for group in groups}
    if len(codes) == 1:
        return next(iter(codes))
    return None


def sync_teacher_specialization_text(teacher_id):
    from portals.models import TeacherProfile

    profile = TeacherProfile.objects.filter(pk=teacher_id).first()
    if not profile:
        return
    labels = profile.get_course_type_labels()
    new_value = ', '.join(labels)
    if profile.specialization != new_value:
        TeacherProfile.objects.filter(pk=teacher_id).update(specialization=new_value)


def validate_teacher_course_codes(codes):
    """Return only codes that exist on active site services."""
    return [code for code in codes if is_active_portal_course_type(code)]

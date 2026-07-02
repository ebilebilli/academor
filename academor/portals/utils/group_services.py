"""Study group ↔ site course (Service) helpers."""

from django.db.models import Count, Q

from portals.utils.portal_services import (
    classroom_service_portal_codes,
    expand_course_types_to_service_slugs,
    services_for_portal_codes,
)


def study_group_portal_codes(group):
    if not group or not group.pk:
        return []
    codes = set(classroom_service_portal_codes(group.courses.all()))
    for slug in group.get_course_slugs():
        if slug:
            codes.add(slug)
    return sorted(codes)


def resolve_group_lesson_service(group):
    """Derive portal course_type for a lesson from the group's linked courses."""
    from portals.utils.portal_services import DEFAULT_PORTAL_SERVICE_CODE

    if not group:
        return DEFAULT_PORTAL_SERVICE_CODE
    codes = study_group_portal_codes(group)
    if codes:
        return codes[0]
    slugs = [slug for slug in group.get_course_slugs() if slug]
    if slugs:
        return slugs[0]
    return DEFAULT_PORTAL_SERVICE_CODE


def study_group_course_slugs(codes):
    return expand_course_types_to_service_slugs(codes or [])


def study_group_courses_filter_q(codes, prefix=''):
    slugs = study_group_course_slugs(codes)
    if not slugs:
        return Q(pk__in=[])
    return Q(**{f'{prefix}courses__slug__in': slugs})


def sync_study_group_courses_from_teacher(group):
    """Link group courses from the teacher's admin-assigned course specializations."""
    from portals.models import TeacherCourseSpecialization

    if not group or not group.teacher_id:
        return
    codes = list(
        TeacherCourseSpecialization.objects.filter(teacher_id=group.teacher_id)
        .values_list('course_type', flat=True)
        .distinct()
    )
    group.courses.set(services_for_portal_codes(codes))


def group_has_portal_code(group, code):
    if not code:
        return False
    return code in set(study_group_portal_codes(group))


def students_matching_group_courses(group):
    """Students with no active enrollments yet, or an active enrollment matching the group."""
    from portals.models import StudentProfile

    if not group or not group.pk:
        return StudentProfile.objects.order_by('user__username', 'id')

    codes = study_group_portal_codes(group)
    qs = StudentProfile.objects.annotate(
        _active_services=Count(
            'course_specializations',
            filter=Q(course_specializations__is_active=True),
            distinct=True,
        ),
    )
    if codes:
        qs = qs.filter(
            Q(_active_services=0)
            | Q(
                course_specializations__course_type__in=codes,
                course_specializations__is_active=True,
            ),
        ).distinct()
    elif group.teacher_id:
        qs = qs.filter(
            Q(_active_services=0)
            | Q(groups__teacher_id=group.teacher_id, groups__is_active=True),
        ).distinct()
    else:
        qs = qs.filter(_active_services=0)
    return qs.select_related('user').order_by('user__username', 'id')


# Backward-compatible aliases.
study_group_service_slugs = study_group_course_slugs
study_group_services_filter_q = study_group_courses_filter_q
sync_study_group_services_from_teacher = sync_study_group_courses_from_teacher

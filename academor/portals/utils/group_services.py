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
    return sorted(classroom_service_portal_codes(group.courses.all()))


def study_group_teaching_portal_codes(group):
    """Portal course codes for teaching services linked on the group (excludes mock SKUs)."""
    if not group or not group.pk:
        return []
    services = [
        service
        for service in group.courses.all()
        if not getattr(service, 'is_mock_test', False)
    ]
    return sorted(classroom_service_portal_codes(services))


def study_group_portal_display_labels(group, lang=None):
    """Human labels for portal course types keyed on the group (deduped)."""
    from portals.utils.portal_services import resolve_course_type_label

    labels = []
    seen = set()
    for code in study_group_teaching_portal_codes(group):
        if code in seen:
            continue
        seen.add(code)
        label = resolve_course_type_label(code, lang=lang)
        if label:
            labels.append(label)
    return labels


def resolve_group_lesson_service(group):
    """Derive portal course_type for a lesson from the group's linked courses."""
    from portals.utils.portal_services import (
        DEFAULT_PORTAL_SERVICE_CODE,
        infer_course_type_for_service,
        normalize_portal_course_type,
    )

    if not group:
        return DEFAULT_PORTAL_SERVICE_CODE

    for service in group.courses.all():
        if getattr(service, 'is_mock_test', False):
            continue
        code = infer_course_type_for_service(service)
        if code:
            return code
        slug = (service.slug or '').strip()
        if slug:
            return normalize_portal_course_type(slug) or slug

    return DEFAULT_PORTAL_SERVICE_CODE


def lesson_effective_subject(lesson):
    """Portal course code used for lesson lists, filters, and labels."""
    from portals.utils.portal_services import normalize_portal_course_type

    stored = normalize_portal_course_type(lesson.subject) or (lesson.subject or '')
    group = getattr(lesson, 'group', None)
    if not group or not getattr(group, 'pk', None):
        return stored

    group_codes = study_group_teaching_portal_codes(group)
    if len(group_codes) == 1:
        return group_codes[0]

    if stored and stored in group_codes:
        return stored
    resolved = resolve_group_lesson_service(group)
    return resolved or stored


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
    """Students eligible for this group (including multi-group enrollment).

    Include students with no enrollments yet, matching course enrollments,
    or membership in any active study group (so a second group can be added).
    """
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
        _active_groups=Count(
            'groups',
            filter=Q(groups__is_active=True),
            distinct=True,
        ),
    )
    eligible = Q(_active_services=0) | Q(_active_groups__gt=0)
    if codes:
        eligible |= Q(
            course_specializations__course_type__in=codes,
            course_specializations__is_active=True,
        )
    return qs.filter(eligible).distinct().select_related('user').order_by('user__username', 'id')


# Backward-compatible aliases.
study_group_service_slugs = study_group_course_slugs
study_group_services_filter_q = study_group_courses_filter_q
sync_study_group_services_from_teacher = sync_study_group_courses_from_teacher

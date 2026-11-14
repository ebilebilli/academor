"""Data for the teacher's Students page: every student of the teacher, filterable by group."""

from django.db.models import Count, Prefetch, Q

from portals.models import StudentCourseSpecialization, StudyGroup
from portals.utils.portal_services import normalize_portal_course_type, resolve_course_type_label
from portals.utils.teacher_courses import teacher_groups_queryset
from portals.utils.teacher_students import teacher_students_qs

GROUP_FILTER_ALL = 'all'
GROUP_FILTER_NONE = 'none'


def resolve_group_filter(raw, group_ids):
    raw = (raw or '').strip()
    if raw == GROUP_FILTER_NONE:
        return GROUP_FILTER_NONE
    if raw.isdigit() and int(raw) in group_ids:
        return int(raw)
    return GROUP_FILTER_ALL


def build_teacher_students_page(teacher_id, *, group_filter=GROUP_FILTER_ALL):
    """Groups (names + counts) and the teacher's active students with their groups and services."""
    groups_qs = (
        teacher_groups_queryset(teacher_id, active_only=True)
        .annotate(
            student_count=Count('students', filter=Q(students__is_active=True), distinct=True),
        )
        .order_by('name', 'id')
    )
    groups = [
        {'id': group.pk, 'name': group.name, 'student_count': group.student_count}
        for group in groups_qs
    ]
    group_ids = [group['id'] for group in groups]
    active_filter = resolve_group_filter(str(group_filter), set(group_ids))

    students_qs = (
        teacher_students_qs(teacher_id)
        .select_related('user')
        .prefetch_related(
            Prefetch(
                'groups',
                queryset=StudyGroup.objects.filter(pk__in=group_ids).order_by('name', 'id'),
                to_attr='teacher_groups',
            ),
            Prefetch(
                'course_specializations',
                queryset=StudentCourseSpecialization.objects.filter(is_active=True),
                to_attr='active_services',
            ),
        )
        .order_by('user__username', 'id')
    )

    rows = []
    for student in students_qs:
        member_groups = [{'id': group.pk, 'name': group.name} for group in student.teacher_groups]
        codes = []
        for row in student.active_services:
            code = normalize_portal_course_type(row.course_type) or row.course_type
            if code and code not in codes:
                codes.append(code)
        rows.append({
            'id': student.pk,
            'full_name': student.full_name,
            'phone': student.phone,
            'can_sign_in': student.user.has_usable_password(),
            'groups': member_groups,
            'group_ids': [group['id'] for group in member_groups],
            'services': [resolve_course_type_label(code) for code in sorted(codes)],
        })

    total = len(rows)
    without_group = sum(1 for row in rows if not row['group_ids'])
    if active_filter == GROUP_FILTER_NONE:
        visible = [row for row in rows if not row['group_ids']]
    elif active_filter == GROUP_FILTER_ALL:
        visible = rows
    else:
        visible = [row for row in rows if active_filter in row['group_ids']]

    return {
        'groups': groups,
        'students': visible,
        'total_students': total,
        'without_group_count': without_group,
        'active_group_filter': active_filter,
        'active_group': next((g for g in groups if g['id'] == active_filter), None),
    }


def set_student_teacher_groups(teacher_id, student, group_ids):
    """Put a student in exactly these of the teacher's groups (other teachers' groups untouched)."""
    own = {
        group.pk: group
        for group in teacher_groups_queryset(teacher_id, active_only=True)
    }
    wanted = {int(pk) for pk in group_ids if str(pk).isdigit() and int(pk) in own}
    current = set(student.groups.filter(pk__in=own.keys()).values_list('pk', flat=True))
    for pk in current - wanted:
        own[pk].students.remove(student)
    full = []
    for pk in wanted - current:
        group = own[pk]
        if group.max_students and group.students.count() >= group.max_students:
            full.append(group.name)
            continue
        group.students.add(student)
    return {
        'group_ids': sorted(student.groups.filter(pk__in=own.keys()).values_list('pk', flat=True)),
        'full_groups': full,
    }
